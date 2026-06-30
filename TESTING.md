# Testing Report

**Date:** 2026-06-30
**Target:** OBSDN staging testnet (`nova.staging.obsdn.trade`, `pulse.staging.obsdn.trade`)
**Result:** 32 passed, 2 skipped, 0 failed (18s)

## Test Summary

| Suite | Tests | Status | Notes |
|-------|-------|--------|-------|
| HMAC Auth | 4 | PASS | Golden vectors match Go backend |
| E2E Staging | 1 | PASS | Full exchange flow with fresh wallet |
| REST Staging | 6 | 4 PASS, 2 SKIP | Skips need pre-set `OBSDN_TEST_API_KEY` |
| Decimal Scale | 8 | PASS | x18 encoding, edge cases, rejections |
| EIP-712 Signing | 10 | PASS | All golden vectors match Rust SDK byte-for-byte |
| WebSocket Staging | 3 | PASS | Book snapshot, ticker, cache population |

## E2E Integration Flow (test_e2e_staging.py)

Full exchange lifecycle with a fresh random wallet against staging:

| Step | Operation | Result |
|------|-----------|--------|
| 1 | Register signer (EIP-712 Register + DelegatedSigner signatures) | PASS - returns api_key + api_secret |
| 2 | Faucet 1000 USDC (on-chain mint, polls portfolio until deposit processed) | PASS - free_coll = 1000 |
| 3 | Place limit order (BTC-PERP BUY 0.001 @ $50,000) | PASS - returns oid |
| 4 | Cancel order by oid | PASS |
| 5 | Withdraw 2 USDC | PASS |

## EIP-712 Signing Vectors (test_sign.py)

Golden fixtures copied from Rust SDK (`tests/fixtures/eip712/`). Each test verifies domain separator, struct hash, digest, and final signature match byte-for-byte.

| Template | Status |
|----------|--------|
| order | PASS |
| transfer | PASS |
| withdraw | PASS |
| create_vault | PASS |
| stake_vault | PASS |
| unstake_vault | PASS |
| create_subaccount | PASS |
| register_signed_by_sender | PASS |
| register_signed_by_signer | PASS |
| register_child_account_signer | PASS |

## HMAC Auth (test_auth.py)

| Test | What it verifies |
|------|-----------------|
| test_matches_go_hmac_format | HMAC-SHA256 signature matches Go backend golden vector |
| test_empty_body | Empty body handling (GET requests) |
| test_place_order_golden | PlaceOrder request signing matches backend expectation |
| test_lowercase_method_normalized | HTTP method case normalization |

## WebSocket (test_ws_staging.py)

Live connection to `wss://pulse.staging.obsdn.trade/ws`:

| Test | What it verifies |
|------|-----------------|
| test_ws_book_snapshot | Subscribe book channel, receive snapshot with bids/asks |
| test_ws_ticker | Subscribe ticker channel, receive market ticker data |
| test_ws_cache_populated | MarketDataCache populates from WS, mid_price/spread work |

## Skipped Tests

| Test | Reason |
|------|--------|
| test_get_portfolio | Needs `OBSDN_TEST_API_KEY` env var |
| test_list_open_orders | Needs `OBSDN_TEST_API_KEY` env var |

These are covered by the e2e test which registers its own credentials.

## Bugs Found and Fixed During Testing

| Bug | Fix |
|-----|-----|
| Withdraw sent `token` field, API expects `tkn` | Fixed in `obsdn/rest/account.py` |
| Transfer missing `from` field | Fixed in `obsdn/rest/account.py` |
| Portfolio `free_coll` nested under `portfolio` key | Fixed in e2e test field access |
| Order response uses `ord.oid` not `order.oid` | Fixed in e2e test |
| Off-chain faucet (`on_chain=False`) not reflected in matching engine | Use `on_chain=True` + poll |
