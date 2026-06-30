from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Env(str, Enum):
    STAGING = "staging"
    PRODUCTION = "production"

    @property
    def rest_base_url(self) -> str:
        if self == Env.STAGING:
            return "https://nova.staging.obsdn.trade"
        return "https://api.obsdn.trade"

    @property
    def ws_url(self) -> str:
        if self == Env.STAGING:
            return "wss://pulse.staging.obsdn.trade/ws"
        return "wss://pulse.obsdn.trade/ws"


@dataclass(frozen=True)
class CustomEnv:
    rest: str
    ws: str

    @property
    def rest_base_url(self) -> str:
        return self.rest.rstrip("/")

    @property
    def ws_url(self) -> str:
        return self.ws
