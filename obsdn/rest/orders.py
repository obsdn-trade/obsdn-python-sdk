from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from obsdn.error import SignError
from obsdn.rest.base import RestClient
from obsdn.sign.scale import scale_decimal_str
from obsdn.types import OrderSide, OrderType, SelfTradePrevention, TimeInForce

if TYPE_CHECKING:
    from obsdn.client import Client


@dataclass
class LimitOrder:
    mkt_id: str
    side: OrderSide
    price: str
    size: str
    tif: TimeInForce = TimeInForce.GTC
    post_only: bool = False
    reduce_only: bool = False
    stp: SelfTradePrevention = SelfTradePrevention.CANCEL_TAKER
    client_order_id: str | None = None
    nonce: int = 0
    await_match: bool = False


class Orders:
    def __init__(self, rest: RestClient, client: Client):
        self._rest = rest
        self._client = client

    async def place(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self._rest.post("/orders", req)

    async def place_group(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self._rest.post("/orders/group", req)

    async def place_twap(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self._rest.post("/orders/twap", req)

    async def cancel(self, oid: str) -> dict[str, Any]:
        return await self._rest.delete(f"/orders/{oid}")

    async def cancel_by_client_id(self, cl_oid: str) -> dict[str, Any]:
        return await self._rest.delete(f"/orders/by-client-id/{cl_oid}")

    async def cancel_many(self, req: dict[str, Any]) -> dict[str, Any]:
        return await self._rest.delete_with_body("/orders", req)

    async def cancel_all(self, mkt_id: str | None = None) -> dict[str, Any]:
        params = {}
        if mkt_id:
            params["mkt_id"] = mkt_id
        return await self._rest.delete_with_query("/orders/all", params)

    async def get(self, oid: str) -> dict[str, Any]:
        return await self._rest.get(f"/orders/{oid}")

    async def get_by_client_id(self, cl_oid: str) -> dict[str, Any]:
        return await self._rest.get(f"/orders/by-client-id/{cl_oid}")

    async def list_open(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/orders", params)

    async def list_history(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/orders/history", params)

    async def place_limit(self, order: LimitOrder) -> dict[str, Any]:
        """One-call resolve -> sign -> place for LIMIT orders."""
        from obsdn.sign.order import sign_order

        size_x18 = scale_decimal_str(order.size)
        price_x18 = scale_decimal_str(order.price)
        if size_x18 == 0:
            raise SignError("order size must be positive")
        if price_x18 == 0:
            raise SignError("order price must be positive")

        market = await self._client.resolve_market(order.mkt_id)
        market_index = int(market["idx"])
        nonce = order.nonce or time.time_ns()

        side_int = 0 if order.side == OrderSide.BUY else 1

        sig = sign_order(
            signer_key=self._client._signer_key,
            domain=self._client._eip712_domain,
            sender=self._client._sender_address,
            market_index=market_index,
            side=side_int,
            size=size_x18,
            price=price_x18,
            nonce=nonce,
        )

        req = {
            "mkt_id": order.mkt_id,
            "sd": order.side.value,
            "ot": OrderType.LIMIT.value,
            "sz": order.size,
            "px": order.price,
            "tif": order.tif.value,
            "po": order.post_only,
            "ro": order.reduce_only,
            "stp": order.stp.value,
            "cl_oid": order.client_order_id or "",
            "nonce": nonce,
            "sig": sig,
            "await": order.await_match,
        }
        return await self.place(req)
