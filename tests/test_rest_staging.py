"""REST smoke tests against staging testnet."""
from __future__ import annotations

import pytest

from obsdn.error import ApiError, AuthError
from obsdn.client import Client
from obsdn.env import Env
from tests.conftest import skip_no_creds


@pytest.mark.asyncio
async def test_get_markets(public_client):
    markets = await public_client.markets().list()
    assert len(markets) > 0
    m = markets[0]
    assert "mkt_id" in m
    assert "mark_px" in m


@pytest.mark.asyncio
async def test_get_orderbook(public_client):
    markets = await public_client.markets().list()
    mkt_id = markets[0]["mkt_id"]
    ob = await public_client.markets().orderbook(mkt_id)
    book = ob.get("book", ob)
    assert "bids" in book or "asks" in book


@pytest.mark.asyncio
async def test_get_assets(public_client):
    assets = await public_client.asset().list()
    assert assets is not None


@pytest.mark.asyncio
async def test_get_chain_config(public_client):
    chain = await public_client.chain().config()
    assert "chain_id" in chain or "addrs" in chain


@pytest.mark.asyncio
async def test_auth_required_without_key():
    async with Client(env=Env.STAGING) as client:
        with pytest.raises(AuthError):
            await client.portfolio().get()


@skip_no_creds
@pytest.mark.asyncio
async def test_get_portfolio(auth_client):
    portfolio = await auth_client.portfolio().get()
    assert portfolio is not None


@skip_no_creds
@pytest.mark.asyncio
async def test_list_open_orders(auth_client):
    result = await auth_client.orders().list_open()
    assert result is not None
