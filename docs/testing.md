# Testing Report

**Date:** 2026-07-09
**Target:** OBSDN staging testnet (`nova.staging.obsdn.trade`, `pulse.staging.obsdn.trade`)

## Running

```bash
make test          # offline suites, no network
make test.staging  # hits live staging
make check         # lint + offline tests + wheel build
```

`make check` deliberately excludes the staging suites so it stays green when
staging is unreachable.

## Test Summary

| Suite | Tests | Network | Status |
|-------|-------|---------|--------|
| HMAC Auth (test_auth.py) | 4 | no | PASS |
| Decimal Scale (test_scale.py) | 9 | no | PASS |
| EIP-712 Signing (test_sign.py) | 10 | no | PASS |
| E2E Staging (test_e2e_staging.py) | 6 | yes | PASS |
| WebSocket Staging (test_ws_staging.py) | 3 | yes | PASS |

32 tests total: 23 offline, 9 against staging.

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
| 4 | Place limit order (BTC-PERP BUY 0.001 @ $50,000) | PASS |
| 5 | List open orders (verify placed order present) | PASS |
| 6 | Cancel order by oid | PASS |
| 7 | Withdraw 2 USDC | PASS |

## EIP-712 Signing (test_sign.py)

Golden fixtures from Rust SDK. Each verifies domain separator, struct hash,
digest, and signature byte-for-byte: order, transfer, withdraw, create_vault,
stake_vault, unstake_vault, create_subaccount, register_signed_by_sender,
register_signed_by_signer, register_child_account_signer.

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

### Wire fields observed live

Confirmed against staging book frames on 2026-07-09: envelope `ts` arrives as a
quoted nanosecond string, `checksum` as an int on book `data`.

`update_reason` is not covered. The backend sets it only on portfolio and
position updates, both private channels, and no test subscribes to them with a
state change in flight.

## Known coverage gaps

**Delegated signers are untested.** `fresh_wallet` registers a signer whose
address equals the account address, so `sender` and the signer coincide. Real
users who create a signer from the API Keys page get distinct addresses, and
must pass `sender` explicitly. That path has no test, which is how examples
shipped omitting `sender` and failing with `invalid order signature`.

Closing this needs a fixture that registers a signer against a separate main
account, then places an order with `sender` set to the main account.
