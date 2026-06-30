"""Place a limit order on OBSDN staging testnet."""
import asyncio
import os

from obsdn.client import Client
from obsdn.env import Env
from obsdn.rest.orders import LimitOrder
from obsdn.types import OrderSide


async def main():
    async with Client(
        env=Env.STAGING,
        api_key=os.environ["OBSDN_API_KEY"],
        api_secret=os.environ["OBSDN_API_SECRET"],
        private_key=os.environ["OBSDN_PRIVATE_KEY"],
    ) as client:
        markets = await client.markets().list()
        print(f"{len(markets)} markets available")

        order = await client.orders().place_limit(LimitOrder(
            mkt_id="BTC-PERP",
            side=OrderSide.BUY,
            price="50000",
            size="0.001",
        ))
        print(f"Order placed: {order}")


if __name__ == "__main__":
    asyncio.run(main())
