# Wallet Funding Status - IMPORTANT UPDATE

## ✅ Purchase Wallet - FUNDED
**Transaction Hash:** `35a7fad72e57951d9f69c34b6647f98e9cb0b87376e11f3bc33b03d71696474d`

The purchase wallet has been successfully funded with test ADA.

## ⚠️ Selling Wallet Address - Use Container Logs

**The wallet addresses need to be derived from the mnemonics by the Masumi containers.**

### Steps to Get Correct Addresses:

1. **Start Masumi services:**
   ```powershell
   docker compose up masumi-payment-service masumi-registry-service
   ```

2. **Watch container logs for wallet addresses:**
   ```powershell
   docker compose logs -f masumi-payment-service | Select-String "address"
   ```

3. **The containers will print the actual preprod addresses** derived from the mnemonics in `.env`

4. **Copy those addresses and fund them via the faucet**

---

## Why Manual Address Derivation Doesn't Work

Cardano addresses require proper key derivation using the BIP32/BIP39 standard with Cardano-specific parameters. The Masumi payment service handles this correctly when it starts up with the configured mnemonics.

**Both wallet mnemonics are already configured in:**
- `.env` (root)
- `masumi-services/.env`

Just start the containers and use the addresses they print in the logs.
