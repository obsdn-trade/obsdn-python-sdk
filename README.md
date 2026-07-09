# OBSDN Python SDK

Python SDK for the [OBSDN](https://obsdn.trade) perpetual exchange. Async-first, with EIP-712 signing abstracted and a real-time market data cache.

## Install

```bash
pip install obsdn-sdk
```

## Quick Start

### Read-only (market data, portfolio)

```python
import asyncio
from obsdn.client import Client
from obsdn.env import Env

async def main():
    async with Client(
        env=Env.STAGING,
        api_key="your-api-key",
        api_secret="your-api-secret",
    ) as client:
        markets = await client.markets().list()
        print(f"{len(markets)} markets")

        portfolio = await client.portfolio().get()

asyncio.run(main())
```

### Trading (requires signer key for EIP-712 signing)

If your signer key was registered as a delegated signer, its address differs
from your main account. Pass `sender` with the main account address, or every
order is rejected with `invalid order signature`. See
[Authentication](#authentication) below.

```python
from obsdn.rest.orders import LimitOrder
from obsdn.types import OrderSide

async with Client(
    env=Env.STAGING,
    api_key="your-api-key",
    api_secret="your-api-secret",
    signer_key="0xYourSignerPrivateKey",
    sender="0xYourMainAccount",  # omit only if signer == main account
) as client:
    order = await client.orders().place_limit(LimitOrder(
        mkt_id="BTC-PERP",
        side=OrderSide.BUY,
        price="50000",
        size="0.001",
    ))
    await client.orders().cancel(order["oid"])
```

## Real-Time Market Data Cache

Run as a long-lived process with instant local state:

```python
async with Client(env=Env.STAGING, ...) as client:
    # Subscribe to WS and populate in-memory cache
    await client.start_cache(markets=["BTC-PERP", "ETH-PERP"])

    # Instant reads from memory (no network round-trip)
    book = client.book("BTC-PERP")
    print(f"mid={book.mid_price}  spread={book.spread}")
    print(f"best bid={book.best_bid}  best ask={book.best_ask}")

    ticker = client.ticker("BTC-PERP")
    oracle = client.oracle_price("BTC")
```

## Authentication

**HMAC (API key/secret)** for REST endpoint authentication:
```python
Client(api_key="...", api_secret="...")
```

**EIP-712 (signer key)** for order/transfer/withdrawal signing:
```python
Client(signer_key="0x...")
```

**Delegated signing** (signer key != sender wallet):
```python
Client(signer_key="0xSignerKey", sender="0xMainWallet")
```

`signer_key` is *who signs*; `sender` is *whose account the order is for*. They
match only when you sign with the main account's own key. If you created the
signer from the API Keys page, they differ, and `sender` is required: the SDK
otherwise defaults it to the signer's own address and the exchange rejects the
order with `invalid order signature`. Both addresses are shown on that page.

## REST API

```python
# Public (no auth)
markets = await client.markets().list()
ob = await client.markets().orderbook("BTC-PERP")
candles = await client.markets().candles("BTC-PERP", resolution="1h")
assets = await client.asset().list()
chain = await client.chain().config()

# Authenticated
portfolio = await client.portfolio().get()
orders = await client.orders().list_open()
history = await client.orders().list_history()

# Trading (requires signer_key for EIP-712 signing)
order = await client.orders().place_limit(LimitOrder(...))
await client.orders().cancel(oid)
await client.orders().cancel_all()

# Transfers
await client.account().transfer(to="0x...", token="0x...", amount="100")
await client.account().withdraw(token="0x...", amount="100")
```

## WebSocket

```python
from obsdn.ws.channel import Channel

session = client.ws()
await session.connect()

# Public channels
stream = await session.subscribe(Channel.book("BTC-PERP"))
async for update in stream:
    print(update.data)

# Private channels (requires api_key/secret)
orders = await session.subscribe(Channel.order())
positions = await session.subscribe(Channel.position())
```

## Environments

| Environment | REST | WebSocket |
|-------------|------|-----------|
| Production | `api.obsdn.trade` | `pulse.obsdn.trade/ws` |
| Staging | `nova.staging.obsdn.trade` | `pulse.staging.obsdn.trade/ws` |

```python
Client(env=Env.PRODUCTION)  # default
Client(env=Env.STAGING)     # testnet
Client(base_url="https://custom", ws_url="wss://custom/ws")  # custom
```

## Examples

See [`examples/`](examples/) for runnable scripts:

- `place_order.py` - place a limit order
- `cancel_order.py` - cancel by order ID
- `ws_book.py` - stream order book with top-of-book display
- `market_maker.py` - simple spread quoting loop
- `ws_private_orders.py` - stream private order updates

## Documentation

- [API Reference](https://docs.obsdn.trade) - REST and WebSocket endpoints
- [Getting Started](https://docs.obsdn.trade/api-ref/guides/getting-started) - integration flow
- [Signing Guide](https://docs.obsdn.trade/api-ref/guides/signing) - EIP-712 payloads
