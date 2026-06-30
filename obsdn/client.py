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
from obsdn.ws.cache import Book, MarketDataCache, Ticker
from obsdn.ws.channel import Channel
from obsdn.ws.session import Session


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
        self._data_cache = MarketDataCache()
        self._ws_session: Session | None = None

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

    def ws(self) -> Session:
        if self._ws_session is None:
            self._ws_session = Session(self._ws_url, self._hmac, self._data_cache)
        return self._ws_session

    async def start_cache(
        self, markets: list[str] | None = None, private: bool = True
    ) -> None:
        """Subscribe to book + ticker for given markets (or all).
        Populates in-memory cache for instant reads via .book()/.ticker()."""
        session = self.ws()
        await session.connect()

        if markets is None:
            mkts = await self.markets().list()
            markets = [m["mkt_id"] for m in mkts if m.get("enabled")]

        for mkt in markets:
            await session.subscribe(Channel.book(mkt))
            await session.subscribe(Channel.ticker(mkt))

        if private and self._hmac:
            await session.subscribe(Channel.order())
            await session.subscribe(Channel.position())
            await session.subscribe(Channel.portfolio())

    async def stop_cache(self) -> None:
        if self._ws_session:
            await self._ws_session.shutdown()
            self._ws_session = None
        self._data_cache.clear()

    def book(self, market: str) -> Book | None:
        return self._data_cache.book(market)

    def ticker(self, market: str) -> Ticker | None:
        return self._data_cache.ticker(market)

    def oracle_price(self, asset: str) -> float | None:
        return self._data_cache.oracle_price(asset)

    def position(self, market: str) -> dict | None:
        return self._data_cache.position(market)

    async def close(self) -> None:
        await self.stop_cache()
        await self._rest.close()

    async def __aenter__(self) -> Client:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
