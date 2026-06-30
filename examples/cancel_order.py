"""Cancel an order by ID on OBSDN staging testnet."""
import asyncio
import os
import sys

from obsdn.client import Client
from obsdn.env import Env


async def main():
    if len(sys.argv) < 2:
        print("Usage: cancel_order.py <order_id>")
        sys.exit(1)

    oid = sys.argv[1]
    async with Client(
        env=Env.STAGING,
        api_key=os.environ["OBSDN_API_KEY"],
        api_secret=os.environ["OBSDN_API_SECRET"],
    ) as client:
        result = await client.orders().cancel(oid)
        print(f"Cancelled: {result}")


if __name__ == "__main__":
    asyncio.run(main())
