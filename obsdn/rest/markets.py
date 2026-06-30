from __future__ import annotations

from typing import Any

from obsdn.rest.base import AuthMode, RestClient


class Markets:
    def __init__(self, rest: RestClient):
        self._rest = rest

    async def list(self) -> list[dict[str, Any]]:
        data = await self._rest.get("/markets", auth=AuthMode.NONE)
        return data.get("mkts", []) if isinstance(data, dict) else data

    async def orderbook(self, mkt_id: str, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query(
            f"/markets/{mkt_id}/orderbook", params, auth=AuthMode.NONE
        )

    async def candles(self, mkt_id: str, **params: Any) -> Any:
        return await self._rest.get_with_query(
            f"/markets/{mkt_id}/candles", params, auth=AuthMode.NONE
        )

    async def trades(self, mkt_id: str, **params: Any) -> Any:
        return await self._rest.get_with_query(
            f"/markets/{mkt_id}/trades", params, auth=AuthMode.NONE
        )

    async def funding_history(self, mkt_id: str, **params: Any) -> Any:
        return await self._rest.get_with_query(
            f"/markets/{mkt_id}/funding-rate-history", params, auth=AuthMode.NONE
        )

    async def slippage(self, mkt_id: str, **params: Any) -> Any:
        return await self._rest.get_with_query(
            f"/markets/{mkt_id}/slippage", params, auth=AuthMode.NONE
        )
