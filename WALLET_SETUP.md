# Cardano Wallet Setup Instructions

## Automatic Wallet Generation via Masumi

The Masumi payment service will **automatically generate** Cardano wallets on first startup when you leave the mnemonic fields empty in `.env`.

### Steps to Get Wallet Addresses:

1. **Start Masumi Services:**
```powershell
cd C:\Users\dhwin\Project-ParknGo
docker compose up -d masumi-postgres-payment masumi-postgres-registry masumi-payment-service
```

2. **Watch Container Logs for Wallet Generation:**
```powershell
# Monitor payment service logs
docker compose logs -f masumi-payment-service

# Or search specifically for wallet info
docker compose logs masumi-payment-service | Select-String "wallet|mnemonic|address"
```

3. **Look for Output Like This:**
```
[Wallet] Generated new Purchase Wallet for Preprod
  Mnemonic: abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual
  Address: addr_test1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwq2ytjqp

[Wallet] Generated new Selling Wallet for Preprod  
  Mnemonic: zoo zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone vote
  Address: addr_test1vzpwq9prsua5vk87rj8l9aqj3cj3c8xy8dqjqemqzqk0r6g9yx5l0
```

4. **IMMEDIATELY Copy Both:**
   - Purchase Wallet Mnemonic (24 words)
   - Purchase Wallet Address
   - Selling Wallet Mnemonic (24 words) 
   - Selling Wallet Address

5. **Fund the Addresses:**
   Visit **Cardano Preprod Faucet**: https://docs.cardano.org/cardano-testnet/tools/faucet/
   
   Request funds for:
   - **Purchase Wallet Address** → Request 1000 tADA (used for escrow payments)
   - **Selling Wallet Address** → Request 100 tADA (used for transaction fees)

6. **Update Environment Files:**
   
   Edit `C:\Users\dhwin\Project-ParknGo\.env`:
   ```env
   PURCHASE_WALLET_PREPROD_MNEMONIC=abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual
   SELLING_WALLET_PREPROD_MNEMONIC=zoo zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone vote
   ```

   Edit `C:\Users\dhwin\Project-ParknGo\masumi-services\.env`:
   ```env
   PURCHASE_WALLET_PREPROD_MNEMONIC=abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual
   SELLING_WALLET_PREPROD_MNEMONIC=zoo zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone zone vote
   ```

7. **Restart Masumi Services:**
   ```powershell
   docker compose restart masumi-payment-service
   ```

## Important Security Notes

⚠️ **NEVER commit wallet mnemonics to git**  
⚠️ **Store mnemonics in a password manager immediately**  
⚠️ **These are testnet wallets - rotate before production**

## Verification

Check wallet balances after faucet funding:
```powershell
# Install cardano-cli or use Cardano Explorer
# Visit: https://preprod.cardanoscan.io/
# Paste your wallet addresses to verify funding
```

## What Happens Next

Once wallets are funded and mnemonics are in `.env`:
1. Masumi payment service can create escrow contracts
2. Purchase wallet funds get locked in smart contracts
3. Selling wallet submits transaction results
4. Your parking sessions trigger real on-chain payments

---

## Quick Start Commands

```powershell
# 1. Start Masumi stack
docker compose up -d masumi-postgres-payment masumi-postgres-registry masumi-payment-service masumi-registry-service

# 2. Get wallet addresses
docker compose logs masumi-payment-service | Select-String "address"

# 3. Fund wallets at faucet (paste addresses)
# https://docs.cardano.org/cardano-testnet/tools/faucet/

# 4. Update .env files with mnemonics

# 5. Restart services
docker compose restart masumi-payment-service masumi-registry-service

# 6. Start full application
docker compose up
```
