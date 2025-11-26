# Quick Start - Get Wallet Addresses for Faucet

## Problem
The manually derived addresses don't work with the Cardano faucet because proper address derivation requires Cardano-specific cryptographic parameters.

## Solution
Let the Masumi containers generate the addresses from the configured mnemonics.

## Steps

### 1. Start Masumi Services (if Docker is available)
```powershell
cd C:\Users\dhwin\Project-ParknGo
docker compose up -d masumi-postgres-payment masumi-postgres-registry
docker compose up masumi-payment-service masumi-registry-service
```

### 2. Watch Logs for Wallet Addresses
```powershell
docker compose logs -f masumi-payment-service
```

Look for output like:
```
Initialized Purchase Wallet:
  Address: addr_test1q...
  
Initialized Selling Wallet:
  Address: addr_test1q...
```

### 3. Fund Those Addresses
Copy the addresses from the logs and request funds at:
https://docs.cardano.org/cardano-testnet/tools/faucet/

---

## Alternative: Use Auto-Generated Wallets

If you want the system to generate completely new wallets:

1. Remove the mnemonics from `.env` and `masumi-services/.env`:
   ```env
   PURCHASE_WALLET_PREPROD_MNEMONIC=
   SELLING_WALLET_PREPROD_MNEMONIC=
   ```

2. Start the Masumi services - they will generate new random mnemonics

3. Copy the mnemonics from logs and store securely

4. Use the printed addresses for faucet funding

---

## Current Configuration Status

✅ **Mnemonics configured** in both `.env` files  
✅ **Purchase wallet has funds** (transaction confirmed)  
⏳ **Need selling wallet address** from container logs  
⏳ **Fund selling wallet** once address is obtained  

The test mnemonics (`abandon abandon...`) are already in your environment files and will work once the containers derive the proper addresses.
