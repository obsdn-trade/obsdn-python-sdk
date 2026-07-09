from __future__ import annotations

from typing import Any

from obsdn.rest.base import RestClient


class Portfolio:
    def __init__(self, rest: RestClient):
        self._rest = rest

    async def get(self) -> dict[str, Any]:
        return await self._rest.get("/portfolio")

    async def history(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/portfolio/history", params)

    async def pnl_history(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/portfolio/pnl-history", params)

    async def trade_history(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/trade-history", params)

    async def positions_history(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/positions/history", params)

    async def set_leverage(self, mkt_id: str, leverage: str) -> dict[str, Any]:
        return await self._rest.post(f"/positions/{mkt_id}/leverage", {"lev": leverage})

    async def set_margin_mode(self, mkt_id: str, mode: str) -> dict[str, Any]:
        return await self._rest.post(f"/positions/{mkt_id}/margin-mode", {"mode": mode})

    async def transfer_margin(self, mkt_id: str, amount: str) -> dict[str, Any]:
        return await self._rest.post(f"/positions/{mkt_id}/margin", {"amount": amount})
