# Acceptance Tests and Expected DB States

Run these in order after starting the stack.

Prereqs:
- Place `secrets/firebase-adminsdk.json` and set `.env`.

A) Entry creates session

1. POST signed entry:

```powershell
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/entry.json
```

Expected: new `/events/<id>` exists and `/sessions/<session_id>` with:

```json
{
  "vehicle_id": "veh-123",
  "status": "pending",
  "accrued_cents": 0,
  "released_cents": 0
}
```

B) Create payment and fund

1. Create payment:

```powershell
curl -X POST http://localhost:8081/create_payment -H "Content-Type: application/json" -d '{"session_id":"<session_id>"}'
```

Expected: `/payments/<pid>` exists with `funded:false` and session has `payment_id` set.

2. Fund:

```powershell
curl -X POST http://localhost:9000/payments/<payment_id>/fund
```

Expected: `/payments/<pid>/funded` becomes `true` and `/sessions/<session_id>/status` becomes `active`.

C) Metering and release

After ticks (wait or set `TICK_INTERVAL_SECONDS` small): `/sessions/<id>/accrued_cents` increases.
When accrued - released >= `RELEASE_THRESHOLD_CENTS`, expect `/payments/<pid>/releases` to gain entries and `/sessions/<id>/released_cents` to increase, and percent fields updated.

D) Exit finalization

1. POST signed exit:

```powershell
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/exit.json
```

Expected: session `status` becomes `ending`, meter_worker performs final release and sets `status` to `ended`, and `released_cents` equals `accrued_cents`.
