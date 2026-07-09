from __future__ import annotations

from enum import Enum
from typing import Any

import httpx

from obsdn.auth import HmacSigner, current_timestamp
from obsdn.error import ApiError, AuthError

USER_AGENT = "obsdn-sdk-python/0.1.0"
MAX_ERROR_BODY = 4096


class AuthMode(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    NONE = "none"


class RestClient:
    def __init__(
        self,
        base_url: str,
        signer: HmacSigner | None = None,
        timeout: float = 10.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._signer = signer
        self._http = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def get(self, path: str, auth: AuthMode = AuthMode.REQUIRED) -> Any:
        return await self._request("GET", path, auth=auth)

    async def get_with_query(
        self, path: str, params: dict, auth: AuthMode = AuthMode.REQUIRED
    ) -> Any:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        full_path = f"{path}?{qs}" if qs else path
        return await self._request("GET", full_path, auth=auth)

    async def post(
        self, path: str, body: dict | None = None, auth: AuthMode = AuthMode.REQUIRED
    ) -> Any:
        return await self._request("POST", path, body=body, auth=auth)

    async def delete(self, path: str, auth: AuthMode = AuthMode.REQUIRED) -> Any:
        return await self._request("DELETE", path, auth=auth)

    async def delete_with_body(
        self, path: str, body: dict, auth: AuthMode = AuthMode.REQUIRED
    ) -> Any:
        return await self._request("DELETE", path, body=body, auth=auth)

    async def delete_with_query(
        self, path: str, params: dict, auth: AuthMode = AuthMode.REQUIRED
    ) -> Any:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        full_path = f"{path}?{qs}" if qs else path
        return await self._request("DELETE", full_path, auth=auth)

    async def _request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        auth: AuthMode = AuthMode.REQUIRED,
    ) -> Any:
        url = f"{self._base_url}{path}"

        # HMAC signs the path only (no query string), matching gateway verification
        sign_path = path.split("?")[0]

        headers: dict[str, str] = {}
        if body is not None:
            headers["Content-Type"] = "application/json"

        body_bytes = b""
        if body is not None:
            import json

            body_bytes = json.dumps(body).encode()

        signer = self._signer
        if auth == AuthMode.REQUIRED and signer is None:
            raise AuthError("endpoint requires authentication but no api_key was configured")
        if signer is not None and auth != AuthMode.NONE:
            ts = current_timestamp()
            sig = signer.sign(ts, method, sign_path, body_bytes)
            headers["x-api-key"] = signer.api_key
            headers["x-api-timestamp"] = ts
            headers["x-api-signature"] = sig

        resp = await self._http.request(
            method,
            url,
            content=body_bytes if body is not None else None,
            headers=headers,
        )

        if resp.is_success:
            data = resp.json()
            if "data" in data:
                return data["data"]
            return data

        _raise_api_error(resp)


def _raise_api_error(resp: httpx.Response) -> None:
    try:
        parsed = resp.json()
        err = parsed.get("error", {})
        raise ApiError(
            status=resp.status_code,
            code=err.get("code", ""),
            message=err.get("message", str(parsed)),
            ref_code=err.get("ref_code", ""),
            request_id=parsed.get("request_id", ""),
        )
    except (ValueError, KeyError):
        # body was not the expected error envelope; the parse failure adds nothing
        body = resp.text[:MAX_ERROR_BODY]
        raise ApiError(status=resp.status_code, message=body) from None
