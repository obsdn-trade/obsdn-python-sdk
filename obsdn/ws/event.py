from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from obsdn.ws.channel import ChannelName


class EventType(str, Enum):
    SNAPSHOT = "snapshot"
    UPDATE = "update"
    RECONNECTED = "reconnected"
    LAGGED = "lagged"
    UNAUTHORIZED = "unauthorized"
    ERROR = "error"


@dataclass
class Trade:
    id: str
    maker_side: str
    price: str
    size: str
    quote_size: str
    ts: str | None = None


@dataclass
class Update:
    channel: ChannelName
    filter: str
    gsn: int
    data: Any
    event_type: EventType = EventType.UPDATE

    def as_trades(self) -> list[Trade]:
        """Decode data as a list of Trade. Works for both snapshot and update."""
        if not isinstance(self.data, list):
            raise ValueError(f"expected list, got {type(self.data).__name__}")
        return [
            Trade(
                id=t["id"],
                maker_side=t["mkr_sd"],
                price=t["px"],
                size=t["sz"],
                quote_size=t["quote_sz"],
                ts=t.get("ts"),
            )
            for t in self.data
        ]


@dataclass
class Event:
    type: EventType
    channel: ChannelName | None = None
    filter: str = ""
    data: Any = None
    message: str = ""
