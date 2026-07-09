"""Stream private order updates from OBSDN."""

import asyncio
import os

from obsdn.client import Client
from obsdn.env import Env
from obsdn.ws.channel import Channel
from obsdn.ws.event import Event


async def main():
    async with Client(
        env=Env.STAGING,
        api_key=os.environ["OBSDN_API_KEY"],
        api_secret=os.environ["OBSDN_API_SECRET"],
    ) as client:
        session = client.ws()
        await session.connect()
        stream = await session.subscribe(Channel.order())

        print("Streaming private order updates (Ctrl+C to stop)...")
        async for item in stream:
            if isinstance(item, Event):
                print(f"  [event] {item.type.value}: {item.message}")
                continue
            print(f"  [order] gsn={item.gsn} {item.data}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped")
