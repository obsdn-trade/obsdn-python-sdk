from __future__ import annotations

from typing import Any

from obsdn.rest.base import AuthMode, RestClient


class AuthEndpoints:
    def __init__(self, rest: RestClient):
        self._rest = rest

    async def register_signer(
        self,
        sndr_addr: str,
        signer_addr: str,
        sndr_sig: str,
        signer_sig: str,
        nonce: int,
        msg: str,
        nm: str = "",
    ) -> dict[str, Any]:
        return await self._rest.post(
            "/auth/signers",
            {
                "sndr_addr": sndr_addr,
                "signer_addr": signer_addr,
                "sndr_sig": sndr_sig,
                "signer_sig": signer_sig,
                "nonce": str(nonce),
                "msg": msg,
                "nm": nm,
            },
            auth=AuthMode.NONE,
        )

    async def create_api_key(self, nm: str = "") -> dict[str, Any]:
        return await self._rest.post("/auth/api-keys", {"nm": nm})

    async def list_api_keys(self) -> Any:
        return await self._rest.get("/auth/api-keys")

    async def delete_api_keys(self, key_ids: list[str]) -> dict[str, Any]:
        return await self._rest.delete_with_body("/auth/api-keys", {"api_keys": key_ids})
