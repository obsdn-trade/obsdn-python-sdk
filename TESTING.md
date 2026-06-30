# Testing Report

**Date:** 2026-06-30
**Target:** OBSDN staging testnet (`nova.staging.obsdn.trade`, `pulse.staging.obsdn.trade`)

## Test Summary

| Suite | Tests | Status |
|-------|-------|--------|
| HMAC Auth | 4 | PASS |
| E2E Staging (public + authenticated) | 6 | PASS |
| Decimal Scale | 8 | PASS |
| EIP-712 Signing | 10 | PASS |
| WebSocket Staging | 3 | PASS |

## E2E Integration (test_e2e_staging.py)

### Public endpoints (no auth)

| Test | What it verifies |
|------|-----------------|
| test_get_markets | List markets, returns mkt_id + mark_px |
| test_get_orderbook | Fetch orderbook, has bids/asks |
| test_get_assets | List assets |
| test_get_chain_config | Chain config (chain_id, contract addrs) |
| test_auth_required_without_key | Unauthenticated portfolio raises AuthError |

### Full exchange flow (fresh wallet each run)

| Step | Operation | Result |
|------|-----------|--------|
| 1 | Register signer (EIP-712 Register + DelegatedSigner) | PASS - returns api_key + api_secret |
| 2 | Faucet 1000 USDC (on-chain, polls until deposit processed) | PASS |
| 3 | Portfolio check (free_coll, tot_coll_val) | PASS |
| 4 | Place limit order (BTC-PERP BUY 0.001 @ $50,000) | PASS - returns oid |
| 5 | List open orders (verify placed order present) | PASS |
| 6 | Cancel order by oid | PASS |
| 7 | Withdraw 2 USDC | PASS |

## EIP-712 Signing (test_sign.py)

Golden fixtures from Rust SDK. Each verifies domain separator, struct hash, digest, and signature byte-for-byte.

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
| test_place_order_golden | PlaceOrder request signing |
| test_lowercase_method_normalized | HTTP method case normalization |

## WebSocket (test_ws_staging.py)

| Test | What it verifies |
|------|-----------------|
| test_ws_book_snapshot | Subscribe book channel, receive snapshot with bids/asks |
| test_ws_ticker | Subscribe ticker channel, receive market ticker data |
| test_ws_cache_populated | MarketDataCache populates, mid_price/spread work |
