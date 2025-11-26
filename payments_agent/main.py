import json
import os
import time
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Optional

import firebase_admin
import requests
from firebase_admin import credentials, db
from flask import Flask, jsonify, request

app = Flask(__name__)

FIREBASE_CREDS = os.environ.get('FIREBASE_CREDENTIALS_JSON')
FIREBASE_DB_URL = os.environ.get('FIREBASE_DB_URL')
MASUMI_API_BASE_URL = os.environ.get(
    'MASUMI_API_BASE_URL', 'http://masumi-payment-service:3001/api/v1'
).rstrip('/')
MASUMI_API_KEY = os.environ.get('MASUMI_API_KEY')
MASUMI_NETWORK = os.environ.get('MASUMI_NETWORK', 'Preprod')
MASUMI_AGENT_IDENTIFIER = os.environ.get('MASUMI_AGENT_IDENTIFIER')
MASUMI_PAYMENT_POLL_SECONDS = int(
    os.environ.get('MASUMI_PAYMENT_POLL_SECONDS', '30')
)
PAYMENTS_PORT = int(os.environ.get('PAYMENTS_PORT', '8081'))

required_env = [
    ('FIREBASE_CREDENTIALS_JSON', FIREBASE_CREDS),
    ('FIREBASE_DB_URL', FIREBASE_DB_URL),
    ('MASUMI_API_KEY', MASUMI_API_KEY),
    ('MASUMI_AGENT_IDENTIFIER', MASUMI_AGENT_IDENTIFIER),
]
missing = [name for name, value in required_env if not value]
if missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})

payments_ref = db.reference('/payments')
sessions_ref = db.reference('/sessions')

FUNDED_STATES = {
    'FundsLocked',
    'ResultSubmitted',
    'RefundRequested',
    'Disputed',
    'Withdrawn',
    'RefundWithdrawn',
    'DisputedWithdrawn',
}
DEFAULT_TIMEOUT = 30


def _full_url(path: str) -> str:
    if not path.startswith('/'):
        path = f'/{path}'
    return f"{MASUMI_API_BASE_URL}{path}"


def _masumi_headers() -> dict:
    return {
        'token': MASUMI_API_KEY,
        'Content-Type': 'application/json',
    }


def _unwrap_response(payload: dict) -> dict:
    if isinstance(payload, dict) and 'data' in payload and payload['data'] is not None:
        return payload['data']
    return payload


def _iso_in(minutes: int) -> str:
    return (datetime.utcnow() + timedelta(minutes=minutes)).replace(microsecond=0).isoformat() + 'Z'


def _cents_to_lovelace(amount_cents: int) -> str:
    # Treat 1 ADA as 100 cents (simple conversion) and express as lovelace
    return str(int(amount_cents) * 10_000)


def _result_hash(session_id: str, payment_id: str, amount_cents: int, idem: str) -> str:
    payload = {
        'session_id': session_id,
        'payment_id': payment_id,
        'amount_cents': amount_cents,
        'idempotency_key': idem,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8'))
    return digest.hexdigest()


def _fetch_payment_status(blockchain_identifier: str) -> Optional[dict]:
    try:
        resp = requests.post(
            _full_url('/payment/resolve-blockchain-identifier'),
            headers=_masumi_headers(),
            json={
                'blockchainIdentifier': blockchain_identifier,
                'network': MASUMI_NETWORK,
                'includeHistory': 'false',
            },
            timeout=DEFAULT_TIMEOUT,
        )
        if resp.status_code >= 400:
            app.logger.warning(
                'Masumi resolve failed %s: %s',
                resp.status_code,
                resp.text,
            )
            return None
        payload = resp.json()
        return _unwrap_response(payload)
    except requests.RequestException as exc:
        app.logger.warning('Masumi resolve error: %s', exc)
        return None


def _mark_payment_state(payment_id: str, record: dict, status: dict) -> None:
    updates = {'masumi_last_status': status}
    on_chain = status.get('onChainState')
    if on_chain in FUNDED_STATES and not record.get('funded'):
        updates['funded'] = True
        session_id = record.get('session_id')
        if session_id:
            sessions_ref.child(session_id).update({'status': 'active'})
    payments_ref.child(payment_id).update(updates)


def _poll_payments_forever():
    interval = max(5, MASUMI_PAYMENT_POLL_SECONDS)
    while True:
        try:
            payment_snapshot = payments_ref.get() or {}
            for pid, record in payment_snapshot.items():
                if record.get('funded'):
                    continue
                blockchain_identifier = record.get('blockchain_identifier') or pid
                status = _fetch_payment_status(blockchain_identifier)
                if status:
                    _mark_payment_state(pid, record, status)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            app.logger.warning('Payment poller failed: %s', exc)
        time.sleep(interval)


threading.Thread(target=_poll_payments_forever, daemon=True).start()


@app.route('/create_payment', methods=['POST'])
def create_payment():
    body = request.get_json(force=True)
    session_id = body.get('session_id')
    if not session_id:
        return jsonify({'ok': False, 'error': 'missing session_id'}), 400

    session = sessions_ref.child(session_id).get()
    if not session:
        return jsonify({'ok': False, 'error': 'session not found'}), 404

    escrow_cents = int(session.get('escrow_deposit_cents') or 0)
    requested_funds = (
        [{'amount': _cents_to_lovelace(escrow_cents), 'unit': 'lovelace'}]
        if escrow_cents > 0
        else None
    )

    masumi_payload = {
        'inputHash': hashlib.sha256(session_id.encode('utf-8')).hexdigest(),
        'network': MASUMI_NETWORK,
        'agentIdentifier': MASUMI_AGENT_IDENTIFIER,
        'identifierFromPurchaser': uuid.uuid4().hex[:26],
        'payByTime': _iso_in(30),
        'submitResultTime': _iso_in(480),
        'unlockTime': _iso_in(720),
        'externalDisputeUnlockTime': _iso_in(1440),
        'metadata': json.dumps(
            {
                'session_id': session_id,
                'vehicle_id': session.get('vehicle_id'),
                'slot_id': session.get('slot_id'),
            },
            separators=(',', ':'),
        ),
    }
    if requested_funds:
        masumi_payload['RequestedFunds'] = requested_funds

    try:
        resp = requests.post(
            _full_url('/payment/'),
            headers=_masumi_headers(),
            json=masumi_payload,
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.RequestException as exc:
        app.logger.error('Masumi create payment failed: %s', exc)
        return jsonify({'ok': False, 'error': 'masumi create failed'}), 502

    if resp.status_code >= 400:
        app.logger.error('Masumi create payment HTTP %s: %s', resp.status_code, resp.text)
        return jsonify({'ok': False, 'error': 'masumi create failed'}), 502

    masumi_response = _unwrap_response(resp.json()) or {}
    blockchain_identifier = masumi_response.get('blockchainIdentifier') or uuid.uuid4().hex

    payments_ref.child(blockchain_identifier).set(
        {
            'payment_id': blockchain_identifier,
            'session_id': session_id,
            'blockchain_identifier': blockchain_identifier,
            'masumi_payment': masumi_response,
            'funded': False,
            'releases': {},
            'created_ts': int(time.time()),
        }
    )

    sessions_ref.child(session_id).update(
        {
            'payment_id': blockchain_identifier,
            'status': 'awaiting_funding',
            'masumi': {
                'blockchain_identifier': blockchain_identifier,
                'network': MASUMI_NETWORK,
                'agent_identifier': MASUMI_AGENT_IDENTIFIER,
            },
        }
    )

    return (
        jsonify({'ok': True, 'payment_id': blockchain_identifier, 'blockchain_identifier': blockchain_identifier}),
        201,
    )


@app.route('/release', methods=['POST'])
def release():
    body = request.get_json(force=True)
    payment_id = body.get('payment_id')
    amount_cents = int(body.get('amount_cents', 0))
    session_id = body.get('session_id')
    idempotency_key = body.get('idempotency_key')

    if not payment_id or not session_id or amount_cents <= 0 or not idempotency_key:
        return jsonify({'ok': False, 'error': 'missing fields'}), 400

    pay_ref = payments_ref.child(payment_id)
    pay = pay_ref.get()
    if not pay:
        return jsonify({'ok': False, 'error': 'payment not found'}), 404

    if not pay.get('funded'):
        status = _fetch_payment_status(pay.get('blockchain_identifier') or payment_id)
        if status:
            _mark_payment_state(payment_id, pay, status)
            pay = pay_ref.get()
    if not pay or not pay.get('funded'):
        return jsonify({'ok': False, 'error': 'payment not funded yet'}), 409

    releases = pay.get('releases') or {}
    for release_obj in releases.values():
        if release_obj.get('idempotency_key') == idempotency_key:
            return jsonify({'ok': True, 'tx_hash': release_obj.get('tx_hash')}), 200

    blockchain_identifier = pay.get('blockchain_identifier') or payment_id
    submit_hash = _result_hash(session_id, blockchain_identifier, amount_cents, idempotency_key)

    try:
        resp = requests.post(
            _full_url('/payment/submit-result'),
            headers=_masumi_headers(),
            json={
                'network': MASUMI_NETWORK,
                'blockchainIdentifier': blockchain_identifier,
                'submitResultHash': submit_hash,
            },
            timeout=DEFAULT_TIMEOUT,
        )
    except requests.RequestException as exc:
        app.logger.error('Masumi submit result failed: %s', exc)
        return jsonify({'ok': False, 'error': 'masumi release failed'}), 502

    if resp.status_code >= 400:
        app.logger.error('Masumi submit result HTTP %s: %s', resp.status_code, resp.text)
        return jsonify({'ok': False, 'error': 'masumi release failed'}), 502

    result_payload = _unwrap_response(resp.json())
    ts = int(time.time())
    tx_hash = (result_payload or {}).get('CurrentTransaction', {}).get('txHash')

    rel_id = pay_ref.child('releases').push().key
    rel_obj = {
        'amount_cents': amount_cents,
        'tx_hash': tx_hash,
        'ts': ts,
        'idempotency_key': idempotency_key,
        'submit_result_hash': submit_hash,
        'masumi_response': result_payload,
    }
    pay_ref.child('releases').child(rel_id).set(rel_obj)
    pay_ref.update({'masumi_last_status': result_payload})

    def tx_update(sess):
        if not sess:
            return sess
        released = sess.get('released_cents', 0) or 0
        sess['released_cents'] = released + amount_cents
        escrow = sess.get('escrow_deposit_cents', 0) or 0
        accrued = sess.get('accrued_cents', 0) or 0
        sess['percent_escrow_used'] = round((sess['released_cents'] / escrow) * 100, 2) if escrow > 0 else 0.0
        sess['percent_paid_of_accrued'] = round((sess['released_cents'] / accrued) * 100, 2) if accrued > 0 else 0.0
        return sess

    sessions_ref.child(session_id).transaction(tx_update)

    return jsonify({'ok': True, 'tx_hash': tx_hash}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PAYMENTS_PORT)
