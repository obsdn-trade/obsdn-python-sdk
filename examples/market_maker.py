"""Simple market maker that quotes bid/ask around mark price.

WARNING: This is an example only. Real market making requires
proper risk management, inventory control, and hedging.
"""
import asyncio
import os

from obsdn.client import Client
from obsdn.env import Env
from obsdn.rest.orders import LimitOrder
from obsdn.types import OrderSide


MARKET = "BTC-PERP"
SPREAD_BPS = 50  # 0.5% spread
SIZE = "0.001"
INTERVAL = 10  # seconds between re-quotes


async def main():
    async with Client(
        env=Env.STAGING,
        api_key=os.environ["OBSDN_API_KEY"],
        api_secret=os.environ["OBSDN_API_SECRET"],
        private_key=os.environ["OBSDN_PRIVATE_KEY"],
    ) as client:
        # Start real-time cache for instant price reads
        await client.start_cache(markets=[MARKET], private=False)
        await asyncio.sleep(2)  # wait for initial snapshot

        print(f"Market making {MARKET} (Ctrl+C to stop)...")
        while True:
            book = client.book(MARKET)
            if not book or not book.mid_price:
                print("  Waiting for book data...")
                await asyncio.sleep(INTERVAL)
                continue

            mid = book.mid_price
            half_spread = mid * SPREAD_BPS / 10000
            bid_px = f"{mid - half_spread:.0f}"
            ask_px = f"{mid + half_spread:.0f}"

            # Cancel existing orders
            try:
                await client.orders().cancel_all(mkt_id=MARKET)
            except Exception:
                pass

            # Place new quotes
            try:
                bid = await client.orders().place_limit(LimitOrder(
                    mkt_id=MARKET, side=OrderSide.BUY, price=bid_px, size=SIZE, post_only=True,
                ))
                ask = await client.orders().place_limit(LimitOrder(
                    mkt_id=MARKET, side=OrderSide.SELL, price=ask_px, size=SIZE, post_only=True,
                ))
                print(f"  mid={mid:.0f}  bid={bid_px}  ask={ask_px}")
            except Exception as e:
                print(f"  Error: {e}")

            await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped")
