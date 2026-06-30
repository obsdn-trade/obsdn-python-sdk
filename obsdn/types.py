from __future__ import annotations

from enum import Enum


class OrderSide(str, Enum):
    BUY = "ORDER_SIDE_BUY"
    SELL = "ORDER_SIDE_SELL"


class OrderType(str, Enum):
    LIMIT = "ORDER_TYPE_LIMIT"
    MARKET = "ORDER_TYPE_MARKET"
    STOP = "ORDER_TYPE_STOP"
    TWAP = "ORDER_TYPE_TWAP"


class TimeInForce(str, Enum):
    GTC = "TIME_IN_FORCE_GTC"
    IOC = "TIME_IN_FORCE_IOC"
    FOK = "TIME_IN_FORCE_FOK"
    GTT = "TIME_IN_FORCE_GTT"


class SelfTradePrevention(str, Enum):
    CANCEL_TAKER = "SELF_TRADE_PREVENTION_CANCEL_TAKER"
    CANCEL_MAKER = "SELF_TRADE_PREVENTION_CANCEL_MAKER"
    CANCEL_BOTH = "SELF_TRADE_PREVENTION_CANCEL_BOTH"


class StopType(str, Enum):
    STOP_LOSS = "STOP_TYPE_STOP_LOSS"
    TAKE_PROFIT = "STOP_TYPE_TAKE_PROFIT"


class StopPriceType(str, Enum):
    LAST = "STOP_PRICE_TYPE_LAST"
    MARK = "STOP_PRICE_TYPE_MARK"
