import os
import time
import hmac
import hashlib
import json
import uuid
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

FIREBASE_CREDS = os.environ.get('FIREBASE_CREDENTIALS_JSON')
FIREBASE_DB_URL = os.environ.get('FIREBASE_DB_URL')
HMAC_KEY = os.environ.get('HMAC_KEY', '')
INGEST_PORT = int(os.environ.get('INGEST_PORT', '8080'))

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})

def compute_sig(payload: dict) -> str:
    # HMAC over JSON with keys sorted, excluding 'sig'
    obj = {k: v for k, v in payload.items() if k != 'sig'}
    s = json.dumps(obj, separators=(',', ':'), sort_keys=True)
    mac = hmac.new(HMAC_KEY.encode('utf-8'), s.encode('utf-8'), hashlib.sha256)
    return mac.hexdigest()

def percent_fields(session: dict):
    escrow = session.get('escrow_deposit_cents', 0) or 0
    accrued = session.get('accrued_cents', 0) or 0
    released = session.get('released_cents', 0) or 0
    pct_escrow = round((released / escrow) * 100, 2) if escrow > 0 else 0.0
    pct_paid = round((released / accrued) * 100, 2) if accrued > 0 else 0.0
    return pct_escrow, pct_paid

@app.route('/ingest/scan', methods=['POST'])
def ingest_scan():
    payload = request.get_json(force=True)
    if not payload:
        return jsonify({'ok': False, 'error': 'invalid json'}), 400

    sig = payload.get('sig', '')
    try:
        expected = compute_sig(payload)
    except Exception:
        return jsonify({'ok': False, 'error': 'sig compute failed'}), 400

    if not hmac.compare_digest(expected, sig):
        return jsonify({'ok': False, 'error': 'invalid sig'}), 401

    ev_type = payload.get('type')
    vehicle_id = payload.get('vehicle_id')
    slot_id = payload.get('slot_id')
    scanner_id = payload.get('scanner_id')
    rate = int(payload.get('rate_per_min_cents', os.environ.get('DEFAULT_RATE', '10')))
    escrow = int(payload.get('escrow_deposit_cents', os.environ.get('RELEASE_THRESHOLD_CENTS', '10')))
    ts = int(payload.get('ts', int(time.time())))

    # create event
    events_ref = db.reference('/events')
    ev_id = events_ref.push().key
    events_ref.child(ev_id).set({
        'type': ev_type,
        'payload': payload,
        'scanner_id': scanner_id,
        'sig': sig,
        'ts': ts
    })

    sessions_ref = db.reference('/sessions')

    if ev_type == 'entry':
        session_id = uuid.uuid4().hex
        session = {
            'vehicle_id': vehicle_id,
            'slot_id': slot_id,
            'start_ts': ts,
            'end_ts': None,
            'status': 'pending',
            'rate_per_min_cents': rate,
            'accrued_cents': 0,
            'released_cents': 0,
            'escrow_deposit_cents': escrow,
            'payment_id': None,
            'last_tick_ts': None,
            'percent_escrow_used': 0.0,
            'percent_paid_of_accrued': 0.0
        }
        sessions_ref.child(session_id).set(session)
        return jsonify({'ok': True, 'session_id': session_id}), 201

    elif ev_type == 'exit':
        # find active session for vehicle
        all_sessions = sessions_ref.get() or {}
        found = None
        for sid, s in all_sessions.items():
            if s.get('vehicle_id') == vehicle_id and s.get('status') in ('active', 'pending'):
                found = (sid, s)
                break

        if not found:
            return jsonify({'ok': False, 'error': 'no active session'}), 404

        sid, sess = found
        # mark as ending
        updates = {'status': 'ending'}
        sessions_ref.child(sid).update(updates)
        return jsonify({'ok': True, 'session_id': sid}), 200

    else:
        return jsonify({'ok': False, 'error': 'unknown type'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=INGEST_PORT)
