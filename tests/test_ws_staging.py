"""WebSocket smoke tests against staging testnet."""

from __future__ import annotations

import asyncio

import pytest

from obsdn.ws.channel import Channel
from obsdn.ws.event import Event, Update


@pytest.mark.asyncio
async def test_ws_book_snapshot(public_client):
    session = public_client.ws()
    await session.connect()
    try:
        stream = await session.subscribe(Channel.book("BTC-PERP"))
        item = await asyncio.wait_for(stream.__anext__(), timeout=10)
        assert isinstance(item, Update)
        book = public_client.book("BTC-PERP")
        assert book is not None
    finally:
        await session.shutdown()


@pytest.mark.asyncio
async def test_ws_ticker(public_client):
    session = public_client.ws()
    await session.connect()
    try:
        stream = await session.subscribe(Channel.ticker("BTC-PERP"))
        try:
            item = await asyncio.wait_for(stream.__anext__(), timeout=10)
            assert isinstance(item, (Update, Event))
        except asyncio.TimeoutError:
            pass  # ticker may not fire on quiet staging
    finally:
        await session.shutdown()


@pytest.mark.asyncio
async def test_ws_cache_populated(public_client):
    session = public_client.ws()
    await session.connect()
    try:
        await session.subscribe(Channel.book("BTC-PERP"))
        await asyncio.sleep(3)
        book = public_client.book("BTC-PERP")
        assert book is not None
        assert book.bids is not None
    finally:
        await session.shutdown()
