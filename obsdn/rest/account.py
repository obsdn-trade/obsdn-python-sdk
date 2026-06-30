from __future__ import annotations

import time
from typing import Any, TYPE_CHECKING

from obsdn.rest.base import AuthMode, RestClient
from obsdn.sign.scale import scale_decimal_str

if TYPE_CHECKING:
    from obsdn.client import Client


class Account:
    def __init__(self, rest: RestClient, client: Client):
        self._rest = rest
        self._client = client

    async def transfer(self, to: str, token: str, amount: str) -> dict[str, Any]:
        from obsdn.sign.transfer import sign_transfer

        amount_x18 = scale_decimal_str(amount)
        nonce = time.time_ns()
        sig = sign_transfer(
            signer_key=self._client._signer_key,
            domain=self._client._eip712_domain,
            from_addr=self._client._sender_address,
            to_addr=to,
            token=token,
            amount=amount_x18,
            nonce=nonce,
        )
        return await self._rest.post("/transfers/send-funds", {
            "from": self._client._sender_address,
            "to": to,
            "tkn": token,
            "amt": amount,
            "nonce": nonce,
            "sig": sig,
        })

    async def withdraw(self, token: str, amount: str) -> dict[str, Any]:
        from obsdn.sign.withdraw import sign_withdraw

        amount_x18 = scale_decimal_str(amount)
        nonce = time.time_ns()
        sig = sign_withdraw(
            signer_key=self._client._signer_key,
            domain=self._client._eip712_domain,
            sender=self._client._sender_address,
            token=token,
            amount=amount_x18,
            nonce=nonce,
        )
        return await self._rest.post("/transfers/withdraw", {
            "tkn": token,
            "amt": amount,
            "nonce": nonce,
            "sig": sig,
        })

    async def faucet(
        self, usr_addr: str, asset: str, amt: str, on_chain: bool = False
    ) -> dict[str, Any]:
        return await self._rest.post(
            "/faucet",
            {"usr_addr": usr_addr, "asset": asset, "amt": amt, "on_chain": on_chain},
            auth=AuthMode.NONE,
        )

    async def transfer_history(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/transfers/history", params)

    async def withdrawal_requests(self, **params: Any) -> dict[str, Any]:
        return await self._rest.get_with_query("/transfers/withdrawal-requests", params)
