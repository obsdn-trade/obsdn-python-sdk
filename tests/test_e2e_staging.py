"""End-to-end integration test against staging testnet.

Covers public endpoints + full exchange flow with a fresh wallet:
  - Public: markets, orderbook, assets, chain config, auth guard
  - Authenticated: register signer, faucet, portfolio, place order,
    open orders, cancel order, withdraw

Run: pytest tests/test_e2e_staging.py -v -s
"""
from __future__ import annotations

import asyncio
import time

import pytest
from eth_account import Account as EthAccount

from obsdn.client import Client
from obsdn.env import Env
from obsdn.error import AuthError
from obsdn.rest.orders import LimitOrder
from obsdn.sign.domain import get_domain
from obsdn.sign.register import sign_register, sign_delegated_signer
from obsdn.types import OrderSide, TimeInForce


STAGING_DOMAIN = get_domain(Env.STAGING)
STAGING_USDC = "0x0F1c3B7a1598297F22A21AC2561Dea31b8037B2e"
FAUCET_AMOUNT = "1000"
ORDER_SIZE = "0.001"
ORDER_PRICE = "50000"
WITHDRAW_AMOUNT = "2"


@pytest.fixture
def fresh_wallet():
    acct = EthAccount.create()
    return acct.key.hex(), acct.address


# --- Public endpoints (no auth) ---

@pytest.mark.asyncio
async def test_get_markets():
    async with Client(env=Env.STAGING) as client:
        markets = await client.markets().list()
        assert len(markets) > 0
        assert "mkt_id" in markets[0]
        assert "mark_px" in markets[0]


@pytest.mark.asyncio
async def test_get_orderbook():
    async with Client(env=Env.STAGING) as client:
        markets = await client.markets().list()
        ob = await client.markets().orderbook(markets[0]["mkt_id"])
        book = ob.get("book", ob)
        assert "bids" in book or "asks" in book


@pytest.mark.asyncio
async def test_get_assets():
    async with Client(env=Env.STAGING) as client:
        assets = await client.asset().list()
        assert assets is not None


@pytest.mark.asyncio
async def test_get_chain_config():
    async with Client(env=Env.STAGING) as client:
        chain = await client.chain().config()
        assert "chain_id" in chain or "addrs" in chain


@pytest.mark.asyncio
async def test_auth_required_without_key():
    async with Client(env=Env.STAGING) as client:
        with pytest.raises(AuthError):
            await client.portfolio().get()


# --- Full authenticated flow ---

@pytest.mark.asyncio
async def test_full_exchange_flow(fresh_wallet):
    """Register -> faucet -> portfolio -> place order -> list open -> cancel -> withdraw."""
    signer_key, address = fresh_wallet
    nonce = time.time_ns()
    message = "obsdn-python-sdk-e2e-test"

    # Step 1: Register signer (sender = signer for this test)
    sender_sig = sign_register(
        signer_key=signer_key,
        domain=STAGING_DOMAIN,
        sender=address,
        signer=address,
        message=message,
        nonce=nonce,
    )
    signer_sig = sign_delegated_signer(
        signer_key=signer_key,
        domain=STAGING_DOMAIN,
        account=address,
    )

    async with Client(env=Env.STAGING) as public_client:
        reg = await public_client.auth().register_signer(
            sndr_addr=address,
            signer_addr=address,
            sndr_sig=sender_sig,
            signer_sig=signer_sig,
            nonce=nonce,
            msg=message,
            nm="e2e-test-key",
        )
        api_key_data = reg["api_key"]
        api_key = api_key_data["api_key"]
        api_secret = api_key_data["api_secret"]

    assert api_key, "register should return api_key"
    assert api_secret, "register should return api_secret"

    async with Client(
        env=Env.STAGING,
        api_key=api_key,
        api_secret=api_secret,
        signer_key=signer_key,
    ) as client:
        # Step 2: Faucet USDC (on_chain=True so deposit flows through sequencer)
        faucet_resp = await client.account().faucet(
            usr_addr=address,
            asset="USDC",
            amt=FAUCET_AMOUNT,
            on_chain=True,
        )
        assert faucet_resp.get("usr_addr") or faucet_resp is not None

        # Poll until on-chain deposit is processed (horizon scan + sequencer)
        free_coll = 0.0
        for _ in range(30):
            await asyncio.sleep(2)
            resp = await client.portfolio().get()
            free_coll = float(resp.get("portfolio", {}).get("free_coll", 0))
            if free_coll > 0:
                break
        assert free_coll > 0, "deposit not reflected after 60s"

        # Step 3: Portfolio has collateral
        portfolio = resp.get("portfolio", {})
        assert float(portfolio.get("tot_coll_val", 0)) > 0

        # Step 4: Place a limit order (far from market to avoid fills)
        order = await client.orders().place_limit(LimitOrder(
            mkt_id="BTC-PERP",
            side=OrderSide.BUY,
            price=ORDER_PRICE,
            size=ORDER_SIZE,
            tif=TimeInForce.GTC,
        ))
        oid = order.get("oid") or order.get("ord", {}).get("oid")
        assert oid, f"place_limit should return oid, got: {order}"

        # Step 5: List open orders includes the placed order
        open_orders = await client.orders().list_open()
        oids = [o.get("oid") for o in open_orders.get("ords", open_orders.get("orders", []))]
        assert oid in oids, f"placed order {oid} not in open orders {oids}"

        # Step 6: Cancel the order
        cancel = await client.orders().cancel(oid)
        assert cancel is not None

        # Step 7: Withdraw
        withdraw = await client.account().withdraw(
            token=STAGING_USDC,
            amount=WITHDRAW_AMOUNT,
        )
        assert withdraw is not None
