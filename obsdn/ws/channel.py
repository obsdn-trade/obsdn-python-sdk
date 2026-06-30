from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ChannelName(str, Enum):
    ORACLE = "oracle"
    TRADE = "trade"
    BOOK = "book"
    TICKER = "ticker"
    ORDER = "order"
    POSITION = "position"
    PORTFOLIO = "portfolio"
    NOTIFICATION = "notification"
    EVENT = "event"

    @property
    def is_private(self) -> bool:
        return self in (
            ChannelName.ORDER,
            ChannelName.POSITION,
            ChannelName.PORTFOLIO,
            ChannelName.NOTIFICATION,
        )


@dataclass(frozen=True)
class Channel:
    name: ChannelName
    filter: str = ""

    @staticmethod
    def book(market: str) -> Channel:
        return Channel(ChannelName.BOOK, market)

    @staticmethod
    def ticker(market: str) -> Channel:
        return Channel(ChannelName.TICKER, market)

    @staticmethod
    def oracle(asset: str) -> Channel:
        return Channel(ChannelName.ORACLE, asset)

    @staticmethod
    def trade(market: str = "") -> Channel:
        return Channel(ChannelName.TRADE, market)

    @staticmethod
    def order(market: str = "") -> Channel:
        return Channel(ChannelName.ORDER, market)

    @staticmethod
    def position(market: str = "") -> Channel:
        return Channel(ChannelName.POSITION, market)

    @staticmethod
    def portfolio() -> Channel:
        return Channel(ChannelName.PORTFOLIO)

    @staticmethod
    def notification() -> Channel:
        return Channel(ChannelName.NOTIFICATION)

    @staticmethod
    def event(event_type: str = "") -> Channel:
        return Channel(ChannelName.EVENT, event_type)

    def wire_params(self) -> dict[str, Any] | None:
        if self.name == ChannelName.ORACLE:
            return {"asset": self.filter}
        if self.name in (ChannelName.BOOK, ChannelName.TICKER):
            return {"market": self.filter}
        if self.name in (ChannelName.TRADE, ChannelName.ORDER, ChannelName.POSITION):
            return {"market": self.filter} if self.filter else None
        if self.name == ChannelName.EVENT:
            return {"event": self.filter} if self.filter else None
        return None
