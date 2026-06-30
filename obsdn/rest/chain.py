from __future__ import annotations

from typing import Any

from obsdn.rest.base import AuthMode, RestClient


class Chain:
    def __init__(self, rest: RestClient):
        self._rest = rest

    async def config(self) -> dict[str, Any]:
        return await self._rest.get("/chain/config", auth=AuthMode.NONE)
