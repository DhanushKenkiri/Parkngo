# Pre-Generated Cardano Preprod Wallets for Testing

## Purchase Wallet (Needs ~100 tADA for escrow payments)

**Mnemonic (24 words):**
```
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art
```

**Status:** ✅ FUNDED (Transaction: 35a7fad72e57951d9f69c34b6647f98e9cb0b87376e11f3bc33b03d71696474d)

## Selling Wallet (Needs ~10 tADA for transaction fees)

**Mnemonic (24 words):**
```
abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon able
```

**Important:** The Masumi containers will auto-generate wallets from these mnemonics on first start. Use the addresses printed in the container logs, or fund via the faucet using the address below once containers are running.

---

## ⚠️ SECURITY WARNING
These are **TEST MNEMONICS ONLY** - derived from the standard BIP39 test seed.
**NEVER use these for production or real funds!**

For production:
1. Use hardware wallet or secure entropy source
2. Generate unique mnemonics
3. Store in encrypted vault
4. Never commit to version control

---

## Fund These Addresses

Visit: https://docs.cardano.org/cardano-testnet/tools/faucet/

**Fund Purchase Wallet:**
```
addr_test1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwq2ytjqp
```
Request: **1000 tADA**

**Fund Selling Wallet:**
```
addr_test1qq9cqg6jcfjqhpqzl5pr9exzf3qpyfjx2wc7dwhz0h65zxjcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqwaqtxm
```
Request: **100 tADA**

---

## Update Environment Files

After funding, update these files:

### `.env` (root directory)
```env
PURCHASE_WALLET_PREPROD_MNEMONIC=abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art
SELLING_WALLET_PREPROD_MNEMONIC=abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon able
```

### `masumi-services/.env`
```env
PURCHASE_WALLET_PREPROD_MNEMONIC=abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon art
SELLING_WALLET_PREPROD_MNEMONIC=abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon able
COLLECTION_WALLET_PREPROD_ADDRESS=addr_test1qq9cqg6jcfjqhpqzl5pr9exzf3qpyfjx2wc7dwhz0h65zxjcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqwaqtxm
```

---

## Verify Funding

After requesting faucet funds, wait 2-3 minutes then verify:

**Check Purchase Wallet Balance:**
```
https://preprod.cardanoscan.io/address/addr_test1qz2fxv2umyhttkxyxp8x0dlpdt3k6cwng5pxj3jhsydzer3jcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwq2ytjqp
```

**Check Selling Wallet Balance:**
```
https://preprod.cardanoscan.io/address/addr_test1qq9cqg6jcfjqhpqzl5pr9exzf3qpyfjx2wc7dwhz0h65zxjcu5d8ps7zex2k2xt3uqxgjqnnj83ws8lhrn648jjxtwqwaqtxm
```

Both should show the faucet amount (usually 1000 tADA per request).

---

## Next Steps

1. ✅ Fund both addresses via faucet
2. ✅ Wait for blockchain confirmation (~2-3 minutes)
3. ✅ Update `.env` and `masumi-services/.env` with mnemonics
4. ✅ Start the full stack:
   ```powershell
   docker compose up
   ```
5. ✅ Register agent with Masumi registry
6. ✅ Update `MASUMI_AGENT_IDENTIFIER` in `.env`
7. ✅ Test entry/exit flow via Firebase RTDB updates
