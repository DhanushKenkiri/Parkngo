# ParknGo Masumi Cloud Backend

Cloud-only backend (Docker) where Firebase Realtime Database events kick off Masumi escrow flows. No frontend is included.

## Services
- `ingestor`: HMAC-protected scanner ingest to create/update sessions in Firebase RTDB.
- `payments_agent`: talks to the official Masumi payment service (GHCR images) to create escrow payments and release funds.
- `meter_worker`: periodic accrual + release trigger that posts to the payments agent.
- `masumi-payment-service` / `masumi-registry-service`: pulled straight from `ghcr.io/masumi-network/*` and orchestrated through the root `docker-compose.yml`.

## Prerequisites
1. Firebase project with Realtime Database + admin service account JSON saved to `./secrets/firebase-adminsdk.json`.
2. Masumi dev credentials:
	- `ADMIN_KEY` and `ENCRYPTION_KEY` (32 bytes) for the payment service container.
	- `MASUMI_AGENT_IDENTIFIER` issued by the registry.
3. Blockfrost Preprod API key (`BLOCKFROST_API_KEY_PREPROD`).
4. Optional: wallet mnemonics/addresses for purchaser/seller flows (leave blank to let Masumi auto-generate).

## Environment
Copy `.env.example` to `.env` (already provided) and fill **all** placeholders:

```dotenv
MASUMI_API_KEY=masumi_admin_api_key_here
ADMIN_KEY=masumi_admin_key_here
ENCRYPTION_KEY=32_char_encryption_key_here
BLOCKFROST_API_KEY_PREPROD=blockfrost_preprod_key_here
```

Leave wallet mnemonics empty if you want the payment container to generate them on first boot; copy the mnemonics from the container logs to keep funding ability.

## Running locally
```powershell
docker compose pull
docker compose build
docker compose up
```

Notes:
- Firebase admin JSON is bind-mounted into every Python service at `/run/secrets/firebase-adminsdk.json`.
- Masumi registry/payment services have Postgres dependencies baked into the compose file and expose ports `3000/3001` locally for debugging.

## Acceptance test flow
1. Simulate entry (signed POST) to create a session:

	```powershell
	python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/entry.json
	```

2. Create an escrow payment tied to that session:

	```powershell
	curl -X POST http://localhost:8081/create_payment \
	  -H "Content-Type: application/json" \
	  -d '{"session_id":"<session_id>"}'
	```

3. Use the Masumi API/CLI (or payment container logs) to fund the blockchain identifier returned in step 2. Once funds reach `FundsLocked`, the payments agent marks the session `active` automatically.

4. Let the `meter_worker` tick (set `TICK_INTERVAL_SECONDS` low for faster demos). When accrued balance crosses thresholds it will ask the payments agent to submit Masumi results.

5. Simulate exit via another signed POST to `ingestor`. This will finalize the session and release escrow per meter calculations.

## Firebase data layout (minimal)
- `/vehicles/{vehicle_id}`
- `/sessions/{session_id}`
- `/payments/{payment_id}`
- `/events/{event_id}`
- `/audit/{audit_id}`

## Tips
- All currency values are stored as integer cents. Default rate per minute is `10` cents unless overridden on ingest payloads.
- Never commit real credentials. Keep `./secrets` out of git and rotate keys regularly.

## Helpers
- `helpers/hmac_post.py` signs payloads with `HMAC_KEY` from `.env` to mimic scanner hardware.
