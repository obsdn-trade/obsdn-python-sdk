# OBSDN Python SDK

Python SDK for the [OBSDN](https://obsdn.trade) perpetual exchange.

## Install

```bash
pip install obsdn-sdk
```

## Quick Start

```python
import asyncio
from obsdn import Env, OrderSide

async def main():
    from obsdn.client import Client

    async with Client(
        env=Env.STAGING,
        api_key="your-api-key",
        api_secret="your-api-secret",
        private_key="0xYourPrivateKey",
    ) as client:
        markets = await client.markets().list()
        print(f"{len(markets)} markets")

        order = await client.orders().place_limit(
            mkt_id="BTC-PERP",
            side=OrderSide.BUY,
            price="50000",
            size="0.001",
        )
        print(f"Order: {order['oid']}")

asyncio.run(main())
```

## Documentation

See [docs.obsdn.trade](https://docs.obsdn.trade) for full API reference.
