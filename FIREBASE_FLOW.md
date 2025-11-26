# Firebase Realtime Database - Vehicle Entry/Exit Flow

This document explains the complete Firebase structure and how state changes trigger automatic Masumi payments.

## Database Structure

```
/
├── vehicles/
│   └── {vehicle_id}/          # e.g., "TS09AB1234"
│       ├── plate_number
│       ├── owner_name
│       ├── created_ts
│       ├── total_sessions
│       ├── last_session_id
│       ├── entry_events/
│       │   └── {event_id}/
│       │       ├── timestamp
│       │       ├── scanner_id
│       │       ├── slot_assigned
│       │       └── session_created
│       └── exit_events/
│           └── {event_id}/
│               ├── timestamp
│               ├── scanner_id
│               └── session_closed
├── sessions/
│   └── {session_id}/
│       ├── vehicle_id
│       ├── slot_id
│       ├── start_ts
│       ├── end_ts
│       ├── status               # "pending" → "awaiting_funding" → "active" → "ending" → "ended"
│       ├── rate_per_min_cents
│       ├── accrued_cents
│       ├── released_cents
│       ├── escrow_deposit_cents
│       ├── payment_id
│       ├── last_tick_ts
│       ├── percent_escrow_used
│       └── percent_paid_of_accrued
├── payments/
│   └── {payment_id}/
│       ├── payment_id
│       ├── session_id
│       ├── blockchain_identifier
│       ├── funded
│       ├── created_ts
│       ├── masumi_last_status
│       └── releases/
│           └── {release_id}/
│               ├── amount_cents
│               ├── tx_hash
│               ├── ts
│               └── idempotency_key
├── events/
│   └── {event_id}/
│       ├── type                # "entry" or "exit"
│       ├── vehicle_id
│       ├── slot_id
│       ├── scanner_id
│       ├── timestamp
│       ├── rate_per_min_cents
│       └── escrow_deposit_cents
└── parking_config/
    ├── default_rate_per_min_cents
    ├── default_escrow_cents
    ├── release_threshold_cents
    └── release_batch_limit_cents
```

## Automated Flow - Vehicle Entry to Exit

### Step 1: Vehicle Entry (Manual Firebase Update)

Add entry event to Firebase:
```json
{
  "vehicles/TS09AB1234/entry_events/entry_001": {
    "event_id": "entry_001",
    "timestamp": 1732611000,
    "scanner_id": "entry-gate-01",
    "slot_assigned": "P1-A1",
    "session_created": null
  }
}
```

### Step 2: Create Session (Manual or via API)

Call ingestor API or manually create session:
```json
{
  "sessions/session_abc123": {
    "vehicle_id": "TS09AB1234",
    "slot_id": "P1-A1",
    "start_ts": 1732611000,
    "end_ts": null,
    "status": "pending",
    "rate_per_min_cents": 15,
    "accrued_cents": 0,
    "released_cents": 0,
    "escrow_deposit_cents": 500,
    "payment_id": null,
    "last_tick_ts": null,
    "percent_escrow_used": 0,
    "percent_paid_of_accrued": 0
  }
}
```

Update vehicle entry event:
```json
{
  "vehicles/TS09AB1234/entry_events/entry_001/session_created": "session_abc123"
}
```

### Step 3: Create Masumi Payment (Manual Trigger)

Update session status to initiate payment:
```json
{
  "sessions/session_abc123/status": "create_payment"
}
```

**OR** Call payments agent API:
```bash
curl -X POST http://localhost:8081/create_payment \
  -H "Content-Type: application/json" \
  -d '{"session_id":"session_abc123"}'
```

**What happens automatically:**
1. Payments agent creates Masumi escrow payment
2. Updates session: `status: "awaiting_funding"`, adds `payment_id`
3. Creates payment record in `/payments/{payment_id}`

### Step 4: Payment Funding (Automatic)

**Payments agent polls every 30 seconds:**
- Checks Masumi blockchain for funding status
- When funds lock: updates session `status: "active"`, sets `funded: true`

### Step 5: Metering & Releases (Automatic)

**Meter worker runs every 60 seconds:**
- Calculates elapsed time since `start_ts`
- Accrues charges: `accrued_cents = minutes_elapsed × rate_per_min_cents`
- When `accrued_cents - released_cents >= 100`:
  - Calls payments agent `/release` endpoint
  - Submits result to Masumi blockchain
  - Updates `released_cents` in session
  - Adds release record to `/payments/{payment_id}/releases/`

### Step 6: Vehicle Exit (Manual Firebase Update)

Add exit event:
```json
{
  "vehicles/TS09AB1234/exit_events/exit_001": {
    "event_id": "exit_001",
    "timestamp": 1732615200,
    "scanner_id": "exit-gate-01",
    "session_closed": null
  }
}
```

Update session status:
```json
{
  "sessions/session_abc123/status": "ending"
}
```

**What happens automatically:**
1. Meter worker detects `ending` status
2. Triggers final release for remaining balance
3. Updates session: `status: "ended"`, sets `end_ts`
4. Updates exit event: `session_closed: "session_abc123"`

---

## State Change Triggers

### Session Status Flow
```
pending → awaiting_funding → active → ending → ended
```

| Status | Trigger | Automated Action |
|--------|---------|------------------|
| `pending` | Session created | Wait for payment creation |
| `awaiting_funding` | Payment created | Poller checks Masumi every 30s |
| `active` | Funds locked on blockchain | Meter worker accrues charges every 60s, triggers releases |
| `ending` | Exit event created | Final release triggered, session finalized |
| `ended` | Final release complete | No further actions |

### Payment Funded Flow
```
funded: false → funded: true
```

When payment `funded` changes to `true`:
- Session status updates to `active`
- Metering begins automatically
- Releases triggered when thresholds met

---

## Manual Testing Steps

### 1. Import Seed Data
Import `tests/firebase_seed.json` to Firebase Console

### 2. Create Session
```json
// Add to /sessions/
{
  "session_001": {
    "vehicle_id": "TS09AB1234",
    "slot_id": "P1-A1",
    "start_ts": 1732611000,
    "status": "pending",
    "rate_per_min_cents": 15,
    "accrued_cents": 0,
    "released_cents": 0,
    "escrow_deposit_cents": 500,
    "payment_id": null
  }
}
```

### 3. Trigger Payment Creation
Call API or update status:
```json
{
  "sessions/session_001/status": "create_payment"
}
```

### 4. Wait for Automatic Funding Detection
Monitor session status change to `active` (happens automatically when Masumi payment is funded)

### 5. Watch Metering
Check session every minute:
- `accrued_cents` increases
- `released_cents` updates when threshold hit
- Check `/payments/*/releases/` for transaction hashes

### 6. Trigger Exit
```json
{
  "sessions/session_001/status": "ending"
}
```

Wait for automatic finalization to `ended`

---

## Configuration

All timing and thresholds in Firebase `/parking_config/`:
```json
{
  "default_rate_per_min_cents": 15,
  "default_escrow_cents": 500,
  "release_threshold_cents": 100,
  "release_batch_limit_cents": 1000
}
```

Also configured in `.env`:
```env
TICK_INTERVAL_SECONDS=60
RELEASE_THRESHOLD_CENTS=100
RELEASE_BATCH_LIMIT_CENTS=1000
```

---

## Wallet Connection

The funded wallet (transaction `35a7fad72e57951d9f69c34b6647f98e9cb0b87376e11f3bc33b03d71696474d`) is already configured via the test mnemonics in `.env` and `masumi-services/.env`.

When Masumi containers start, they derive the address from the mnemonic and use it for all escrow payments.

**No AI/Gemini needed** - the system is fully automated via Python services monitoring Firebase state changes.
