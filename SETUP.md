# ParknGo Production Setup Guide

## Prerequisites Completed ✓
- ✅ Firebase Realtime Database: `parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app`
- ✅ Blockfrost Preprod API Key: `preprodB89YxEKG3AjAHvYRJFpxtVZSZKjLtXQm`
- ✅ Secure keys generated (ADMIN, ENCRYPTION, HMAC)
- ✅ Docker Compose stack configured for Masumi + Python services

## Setup Steps

### 1. Firebase Service Account
**Action Required:** Download your Firebase Admin SDK private key:
1. Go to [Firebase Console](https://console.firebase.google.com/project/parkngo-ai/settings/serviceaccounts/adminsdk)
2. Click "Generate new private key"
3. Save the downloaded JSON to `secrets/firebase-adminsdk.json` (replacing the placeholder file)

### 2. Start Masumi Services & Generate Wallets
```powershell
# Navigate to project root
cd C:\Users\dhwin\Project-ParknGo

# Start Masumi stack (Postgres + Registry + Payment services)
docker compose up -d masumi-postgres-payment masumi-postgres-registry masumi-registry-service masumi-payment-service

# Watch payment service logs for wallet generation
docker compose logs -f masumi-payment-service
```

**Look for output like:**
```
Generated Purchase Wallet:
  Mnemonic: word1 word2 word3 ... word24
  Address: addr_test1...

Generated Selling Wallet:
  Mnemonic: word25 word26 word27 ... word48
  Address: addr_test1...
```

**Copy both mnemonics and addresses immediately!**

### 3. Fund Wallets via Preprod Faucet
Visit [Cardano Testnet Faucet](https://docs.cardano.org/cardano-testnet/tools/faucet/) and request funds for:
- **Purchase Wallet Address** (needs ~100 tADA for escrow payments)
- **Selling Wallet Address** (needs ~10 tADA for transaction fees)

Paste the wallet addresses you noted from step 2.

### 4. Update Environment with Wallet Mnemonics
After funding, edit both env files:

**Root `.env`:**
```env
PURCHASE_WALLET_PREPROD_MNEMONIC=word1 word2 word3 ... word24
SELLING_WALLET_PREPROD_MNEMONIC=word25 word26 word27 ... word48
```

**`masumi-services/.env`:**
```env
PURCHASE_WALLET_PREPROD_MNEMONIC=word1 word2 word3 ... word24
SELLING_WALLET_PREPROD_MNEMONIC=word25 word26 word27 ... word48
```

### 5. Register Agent with Masumi Registry
```powershell
# Call registry service to create your agent
$headers = @{
    "token" = "f6KDRQMSMhwZRFppQH5AnpAgDLmv-olb"
    "Content-Type" = "application/json"
}

$body = @{
    name = "ParknGo Parking Agent"
    description = "Real-time parking escrow payments"
    network = "Preprod"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:3000/api/v1/agent" -Method Post -Headers $headers -Body $body

# Copy the returned agent identifier
Write-Host "Agent Identifier: $($response.data.agentIdentifier)"
```

**Update `.env` with the returned identifier:**
```env
MASUMI_AGENT_IDENTIFIER=<paste-agent-identifier-here>
```

### 6. Import Test Data to Firebase
1. Open [Firebase Console → Realtime Database](https://console.firebase.google.com/project/parkngo-ai/database/parkngo-ai-default-rtdb/data)
2. Click the three-dot menu → "Import JSON"
3. Select `tests/firebase_seed.json` from this repository
4. Confirm import

### 7. Start Full Application Stack
```powershell
# Pull latest images and build services
docker compose pull
docker compose build

# Start everything
docker compose up
```

**Services will be available at:**
- Ingestor (HMAC-protected): http://localhost:8080
- Payments Agent: http://localhost:8081
- Masumi Registry: http://localhost:3000/docs
- Masumi Payment Service: http://localhost:3001/docs

### 8. Test End-to-End Flow

**Simulate vehicle entry:**
```powershell
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/entry.json
```

**Create escrow payment:**
```powershell
$session_id = "<session-id-from-entry-response>"
curl -X POST http://localhost:8081/create_payment `
  -H "Content-Type: application/json" `
  -d "{\"session_id\":\"$session_id\"}"
```

**Monitor payment status:**
- Check Firebase RTDB for session status updates
- Watch `payments_agent` logs for funding detection
- Meter worker will automatically accrue charges every 60 seconds

**Simulate exit:**
```powershell
python helpers/hmac_post.py --url http://localhost:8080/ingest/scan --file tests/exit.json
```

## Security Checklist
- ✅ `.env` and `masumi-services/.env` excluded from git
- ✅ `secrets/firebase-adminsdk.json` excluded from git
- ✅ Secure random keys generated for HMAC, Admin, Encryption
- ⚠️ **Store wallet mnemonics in secure password manager**
- ⚠️ **Rotate keys before production deployment**

## Faucet Wallet Addresses
**Purchase Wallet:** (paste address from step 2)  
**Selling Wallet:** (paste address from step 2)

Request testnet ADA at: https://docs.cardano.org/cardano-testnet/tools/faucet/

---

## Current Configuration Summary
- **Firebase Project:** parkngo-ai
- **Database URL:** https://parkngo-ai-default-rtdb.asia-southeast1.firebasedatabase.app
- **Network:** Cardano Preprod Testnet
- **Blockfrost Key:** preprodB89YxEKG3AjAHvYRJFpxtVZSZKjLtXQm
- **HMAC Key:** 88df5a004c3ec69d5a96beb5ab4c262802fd0d9c2fbb2951fce4e04ae4e8401b
- **Admin Key:** f6KDRQMSMhwZRFppQH5AnpAgDLmv-olb
- **Encryption Key:** 6da046e8b9f6991eea34e5cb1704edef
