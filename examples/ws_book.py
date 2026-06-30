"""Stream order book from OBSDN and print top-of-book."""
import asyncio

from obsdn.client import Client
from obsdn.env import Env
from obsdn.ws.channel import Channel
from obsdn.ws.event import Update, Event


async def main():
    market = "BTC-PERP"

    async with Client(env=Env.STAGING) as client:
        session = client.ws()
        await session.connect()
        stream = await session.subscribe(Channel.book(market))

        print(f"Streaming {market} book (Ctrl+C to stop)...")
        async for item in stream:
            if isinstance(item, Event):
                print(f"  [event] {item.type.value}")
                continue

            book = client.book(market)
            if book and book.bids and book.asks:
                bid = book.best_bid
                ask = book.best_ask
                mid = book.mid_price
                spread = book.spread
                print(
                    f"  bid={bid[0]}x{bid[1]}  ask={ask[0]}x{ask[1]}  "
                    f"mid={mid:.2f}  spread={spread:.2f}  "
                    f"depth={len(book.bids)}x{len(book.asks)}"
                )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped")
