from __future__ import annotations

from typing import Any

from obsdn.rest.base import AuthMode, RestClient


class Asset:
    def __init__(self, rest: RestClient):
        self._rest = rest

    async def list(self) -> Any:
        return await self._rest.get("/assets", auth=AuthMode.NONE)
