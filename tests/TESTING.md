# Testing Vehicle Entry and Exit Flow

## Prerequisites
1. Ensure all services are running:
   ```powershell
   docker compose up
   ```

2. Verify services are healthy:
   - Ingestor: http://localhost:8080
   - Payments Agent: http://localhost:8081
   - Masumi Payment Service: http://localhost:3001/docs

## Step-by-Step Test Flow

### 1. Simulate Vehicle Entry
This creates a new parking session for vehicle `TS09AB1234`:

```powershell
# From project root directory
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/entry.json
```

**Expected Response:**
```json
{
  "ok": true,
  "session_id": "<new-session-id>"
}
```

**What happens:**
- New session created in Firebase `/sessions/<session_id>`
- Session status: `pending`
- Vehicle entry event logged in `/events/`

### 2. Create Masumi Payment for Session
Use the session_id from step 1:

```powershell
$sessionId = "<paste-session-id-from-entry-response>"

curl -X POST http://localhost:8081/create_payment `
  -H "Content-Type: application/json" `
  -d "{\"session_id\":\"$sessionId\"}"
```

**Expected Response:**
```json
{
  "ok": true,
  "payment_id": "<blockchain-identifier>",
  "blockchain_identifier": "<blockchain-identifier>"
}
```

**What happens:**
- Masumi payment created with escrow of 500 cents (5 ADA equivalent)
- Payment record created in Firebase `/payments/<payment_id>`
- Session updated with `payment_id` and status: `awaiting_funding`

### 3. Monitor Payment Funding (Automatic)
The `payments_agent` polls Masumi every 30 seconds to check if the blockchain payment is funded.

**Check Firebase Realtime Database:**
- Navigate to `/sessions/<session_id>`
- Watch for status change from `awaiting_funding` → `active`
- Check `/payments/<payment_id>` for `funded: true`

**Manual check via Masumi API:**
```powershell
curl -X POST http://localhost:3001/api/v1/payment/resolve-blockchain-identifier `
  -H "token: f6KDRQMSMhwZRFppQH5AnpAgDLmv-olb" `
  -H "Content-Type: application/json" `
  -d "{\"blockchainIdentifier\":\"<blockchain-identifier>\",\"network\":\"Preprod\",\"includeHistory\":\"false\"}"
```

**Note:** For actual funding to occur, the purchase wallet must have sufficient tADA. In development, you can:
- Fund the purchase wallet via preprod faucet
- Wait for Masumi to lock funds in the smart contract
- Or simulate funding by updating Firebase manually (not recommended)

### 4. Metering & Auto-Releases (Automatic)
Once session is `active`, the `meter_worker` runs every 60 seconds:

**What happens automatically:**
- Calculates minutes elapsed since entry
- Accrues charges at 15 cents/minute
- When `accrued_cents - released_cents >= 100` (threshold):
  - Calls `/release` endpoint on payments_agent
  - Submits result to Masumi blockchain
  - Updates `released_cents` in Firebase

**Monitor in Firebase:**
- `/sessions/<session_id>/accrued_cents` increases every minute
- `/sessions/<session_id>/released_cents` increases in batches
- `/payments/<payment_id>/releases/` shows release transactions

### 5. Simulate Vehicle Exit
After some time has passed (let metering run for a few minutes):

```powershell
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/exit.json
```

**Expected Response:**
```json
{
  "ok": true,
  "session_id": "<session-id>"
}
```

**What happens:**
- Session status changes to `ending`
- Meter worker detects `ending` status
- Final release triggered for any remaining unpaid balance
- Session marked as `ended` with `end_ts` timestamp

### 6. Verify Final State in Firebase
Check `/sessions/<session_id>`:
```json
{
  "status": "ended",
  "end_ts": <timestamp>,
  "accrued_cents": <total-charges>,
  "released_cents": <total-paid>,
  "percent_escrow_used": <percentage>,
  "percent_paid_of_accrued": 100.0
}
```

Check `/payments/<payment_id>/releases/`:
- Should show multiple release transactions
- Each with `tx_hash` from Masumi blockchain
- Final release should match remaining balance

## Troubleshooting

### Session Not Created
**Issue:** Entry POST returns 401 "invalid sig"
**Solution:** The HMAC signature is computed automatically by `hmac_post.py` using the `HMAC_KEY` from `.env`. Verify:
```powershell
cat .env | Select-String HMAC_KEY
```

### Payment Not Funded
**Issue:** Session stuck in `awaiting_funding`
**Solution:** 
1. Check purchase wallet balance:
   ```powershell
   # Get wallet address from Masumi logs
   docker compose logs masumi-payment-service | Select-String "address"
   ```
2. Fund via faucet: https://docs.cardano.org/cardano-testnet/tools/faucet/
3. Wait 2-3 minutes for blockchain confirmation

### No Metering
**Issue:** `accrued_cents` not increasing
**Solution:**
1. Check meter_worker logs:
   ```powershell
   docker compose logs meter_worker
   ```
2. Verify `TICK_INTERVAL_SECONDS` in `.env` (default 60 seconds)
3. Ensure session status is `active`

### Releases Failing
**Issue:** `released_cents` not updating
**Solution:**
1. Check payments_agent logs:
   ```powershell
   docker compose logs payments_agent
   ```
2. Verify Masumi payment service is healthy:
   ```powershell
   curl http://localhost:3001/api/v1/health
   ```
3. Ensure payment is funded (`funded: true` in Firebase)

## Quick End-to-End Test Script

```powershell
# 1. Entry
$entryResponse = python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/entry.json | ConvertFrom-Json
$sessionId = $entryResponse.session_id
Write-Host "Session created: $sessionId"

# 2. Create payment
$paymentResponse = curl -X POST http://localhost:8081/create_payment -H "Content-Type: application/json" -d "{\"session_id\":\"$sessionId\"}" | ConvertFrom-Json
$paymentId = $paymentResponse.payment_id
Write-Host "Payment created: $paymentId"

# 3. Wait for funding (check Firebase manually)
Write-Host "Waiting for payment to be funded... Check Firebase RTDB"
Read-Host "Press Enter after session status changes to 'active'"

# 4. Wait for metering (2-3 minutes)
Write-Host "Metering active. Wait 2-3 minutes for charges to accrue..."
Start-Sleep -Seconds 180

# 5. Exit
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/exit.json
Write-Host "Exit processed. Check Firebase for final session state."
```

## Test Data Reference
- **Vehicle ID:** TS09AB1234
- **Slot ID:** P1-A1
- **Rate:** 15 cents/minute
- **Escrow:** 500 cents (5 ADA equivalent in lovelace)
- **Release Threshold:** 100 cents
- **Metering Interval:** 60 seconds
