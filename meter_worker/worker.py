import os
import time
import math
import requests
import firebase_admin
from firebase_admin import credentials, db

FIREBASE_CREDS = os.environ.get('FIREBASE_CREDENTIALS_JSON')
FIREBASE_DB_URL = os.environ.get('FIREBASE_DB_URL')
TICK_INTERVAL = int(os.environ.get('TICK_INTERVAL_SECONDS', '60'))
RELEASE_THRESHOLD = int(os.environ.get('RELEASE_THRESHOLD_CENTS', '100'))
RELEASE_BATCH_LIMIT = int(os.environ.get('RELEASE_BATCH_LIMIT_CENTS', '1000'))
PAYMENTS_AGENT_URL = os.environ.get('PAYMENTS_AGENT_URL', 'http://payments_agent:8081')

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDS)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})

sessions_ref = db.reference('/sessions')

def process_tick():
    now = int(time.time())
    all_sessions = sessions_ref.get() or {}
    for sid, s in all_sessions.items():
        status = s.get('status')
        if status not in ('active', 'ending'):
            continue

        start_ts = s.get('start_ts') or now
        rate = int(s.get('rate_per_min_cents', 10))
        minutes_elapsed = math.floor((now - start_ts) / 60)
        if minutes_elapsed < 0:
            minutes_elapsed = 0
        target_accrued = minutes_elapsed * rate

        def tx_accrued(curr):
            if not curr:
                return curr
            accrued = curr.get('accrued_cents', 0) or 0
            delta = target_accrued - accrued
            if delta > 0:
                curr['accrued_cents'] = accrued + delta
                curr['last_tick_ts'] = now
            return curr

        sessions_ref.child(sid).transaction(tx_accrued)

        # read fresh
        fresh = sessions_ref.child(sid).get() or {}
        accrued = int(fresh.get('accrued_cents', 0) or 0)
        released = int(fresh.get('released_cents', 0) or 0)
        unpaid = accrued - released
        payment_id = fresh.get('payment_id')

        if status == 'ending':
            if unpaid > 0 and payment_id:
                key = f"{sid}-final-{now}"
                try:
                    requests.post(f"{PAYMENTS_AGENT_URL}/release", json={'payment_id': payment_id, 'amount_cents': unpaid, 'session_id': sid, 'idempotency_key': key}, timeout=10)
                except Exception:
                    pass
            # finalize
            sessions_ref.child(sid).update({'status': 'ended', 'end_ts': now})
            continue

        # normal active session
        if unpaid >= RELEASE_THRESHOLD and payment_id:
            to_release = min(unpaid, RELEASE_BATCH_LIMIT)
            key = f"{sid}-{now}"
            try:
                requests.post(f"{PAYMENTS_AGENT_URL}/release", json={'payment_id': payment_id, 'amount_cents': to_release, 'session_id': sid, 'idempotency_key': key}, timeout=10)
            except Exception:
                pass

if __name__ == '__main__':
    while True:
        try:
            process_tick()
        except Exception:
            pass
        time.sleep(TICK_INTERVAL)
