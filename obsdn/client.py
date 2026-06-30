from __future__ import annotations

from typing import Any

from eth_account import Account as EthAccount

from obsdn.auth import HmacSigner
from obsdn.env import Env, CustomEnv
from obsdn.error import ConfigError, SignError
from obsdn.rest.base import RestClient
from obsdn.rest.markets import Markets
from obsdn.rest.orders import Orders
from obsdn.rest.portfolio import Portfolio
from obsdn.rest.account import Account
from obsdn.rest.auth_endpoints import AuthEndpoints
from obsdn.rest.asset import Asset
from obsdn.rest.chain import Chain
from obsdn.sign.domain import get_domain


class Client:
    def __init__(
        self,
        env: Env | CustomEnv | str = Env.PRODUCTION,
        api_key: str | None = None,
        api_secret: str | None = None,
        private_key: str | None = None,
        sender: str | None = None,
        base_url: str | None = None,
        ws_url: str | None = None,
        timeout: float = 10.0,
        eip712_domain: dict | None = None,
    ):
        if isinstance(env, str) and not isinstance(env, Env):
            env = Env(env)

        self._env = env

        if base_url:
            rest_base = base_url.rstrip("/")
        else:
            rest_base = env.rest_base_url

        if ws_url:
            self._ws_url = ws_url
        else:
            self._ws_url = env.ws_url

        hmac = None
        if api_key and api_secret:
            if not api_key or not api_secret:
                raise ConfigError("api_key and api_secret must both be non-empty")
            hmac = HmacSigner(api_key, api_secret)

        self._hmac = hmac
        self._rest = RestClient(rest_base, hmac, timeout)

        self._private_key: str | None = private_key
        self._sender_address: str | None = None
        self._eip712_domain: dict | None = eip712_domain

        if private_key:
            acct = EthAccount.from_key(private_key)
            signer_addr = acct.address
            self._sender_address = sender or signer_addr
            if eip712_domain is None:
                self._eip712_domain = get_domain(env)
        elif sender:
            self._sender_address = sender

        self._market_cache: dict[str, dict] | None = None

    def markets(self) -> Markets:
        return Markets(self._rest)

    def orders(self) -> Orders:
        return Orders(self._rest, self)

    def portfolio(self) -> Portfolio:
        return Portfolio(self._rest)

    def account(self) -> Account:
        return Account(self._rest, self)

    def auth(self) -> AuthEndpoints:
        return AuthEndpoints(self._rest)

    def asset(self) -> Asset:
        return Asset(self._rest)

    def chain(self) -> Chain:
        return Chain(self._rest)

    async def resolve_market(self, mkt_id: str) -> dict[str, Any]:
        if self._market_cache is None:
            mkts = await self.markets().list()
            self._market_cache = {m["mkt_id"]: m for m in mkts}
        mkt = self._market_cache.get(mkt_id)
        if mkt is None:
            raise ConfigError(f"unknown market: {mkt_id}")
        return mkt

    def invalidate_market_cache(self) -> None:
        self._market_cache = None

    async def close(self) -> None:
        await self._rest.close()

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
