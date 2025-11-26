# ParknGo-Cloud-Firebase-Masumi

Overview
- Cloud-only backend (Docker) where Firebase Realtime Database triggers Masumi real-time payments. No frontend.

Contents
- `ingestor`: ingest scanner events, create sessions and events in RTDB.
- `payments_agent`: creates Masumi payments, receives webhooks, performs releases.
- `meter_worker`: per-minute metering, accrual and release triggers.
- `mock_masumi`: local Masumi mock for development.

Quick local setup
1. Copy `.env.example` to `.env` and fill values.
2. Place Firebase service account JSON at `./secrets/firebase-adminsdk.json`.
3. Build and run:

```powershell
docker compose build ; docker compose up
```

Acceptance test flow (examples)

1) Simulate entry (signed POST). Use helper to HMAC-sign and post:

```powershell
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/entry.json
```

2) Create payment for session (payments_agent):

```powershell
curl -X POST http://localhost:8081/create_payment -H "Content-Type: application/json" -d '{"session_id":"<session_id>"}'
```

3) Fund payment in mock Masumi:

```powershell
curl -X POST http://localhost:9000/payments/<payment_id>/fund
```

4) Wait for meter ticks (every minute). You can reduce `TICK_INTERVAL_SECONDS` in `.env` for faster testing.

5) Simulate exit (signed POST):

```powershell
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/exit.json
```

Firebase RTDB structure (minimal)
- `/vehicles/{vehicle_id}`
- `/sessions/{session_id}`
- `/payments/{payment_id}`
- `/events/{event_id}`
- `/audit/{audit_id}`

Notes
- Money values are integer cents. Default rate per minute is `10` cents unless overridden on ingest.
- Secrets must be injected via mounted files or env vars. Do NOT commit service account JSON.

Acceptance test payloads and expected DB states are shown in the `tests/` section below in this README.

Tests and helpers
- `helpers/hmac_post.py` can sign and post payloads with the HMAC key.
