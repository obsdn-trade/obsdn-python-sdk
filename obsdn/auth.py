from __future__ import annotations

import base64
import hashlib
import hmac
import time


class HmacSigner:
    __slots__ = ("_key", "_secret")

    def __init__(self, api_key: str, api_secret: str):
        self._key = api_key
        self._secret = api_secret.encode()

    @property
    def api_key(self) -> str:
        return self._key

    def sign(self, timestamp: str, method: str, path: str, body: bytes = b"") -> str:
        return sign_hmac(self._secret, timestamp, method, path, body)

    def sign_ws(self, timestamp: str) -> str:
        prehash = f"{self._key},{timestamp}"
        mac = hmac.new(self._secret, prehash.encode(), hashlib.sha256)
        return base64.standard_b64encode(mac.digest()).decode()

    def __repr__(self) -> str:
        return f"HmacSigner(key={self._key!r}, secret=<redacted>)"


def sign_hmac(
    secret: bytes,
    timestamp: str,
    method: str,
    path: str,
    body: bytes = b"",
) -> str:
    prehash = timestamp.encode() + method.upper().encode() + path.encode() + body
    mac = hmac.new(secret, prehash, hashlib.sha256)
    return base64.standard_b64encode(mac.digest()).decode()


def current_timestamp() -> str:
    return str(int(time.time()))
