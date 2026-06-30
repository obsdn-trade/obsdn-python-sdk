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
class Update:
    channel: ChannelName
    filter: str
    gsn: int
    data: Any
    event_type: EventType = EventType.UPDATE


@dataclass
class Event:
    type: EventType
    channel: ChannelName | None = None
    filter: str = ""
    data: Any = None
    message: str = ""
