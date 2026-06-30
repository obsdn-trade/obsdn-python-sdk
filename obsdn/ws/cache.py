from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Book:
    bids: list[list[str]] = field(default_factory=list)
    asks: list[list[str]] = field(default_factory=list)
    timestamp: float = 0.0

    @property
    def best_bid(self) -> tuple[str, str] | None:
        return tuple(self.bids[0]) if self.bids else None

    @property
    def best_ask(self) -> tuple[str, str] | None:
        return tuple(self.asks[0]) if self.asks else None

    @property
    def mid_price(self) -> float | None:
        if not self.bids or not self.asks:
            return None
        return (float(self.bids[0][0]) + float(self.asks[0][0])) / 2

    @property
    def spread(self) -> float | None:
        if not self.bids or not self.asks:
            return None
        return float(self.asks[0][0]) - float(self.bids[0][0])


@dataclass
class Ticker:
    market: str = ""
    last_price: str = "0"
    mark_price: str = "0"
    index_price: str = "0"
    best_bid: str = "0"
    best_ask: str = "0"
    volume_24h: str = "0"
    change_24h: str = "0"
    funding_rate: str = "0"
    open_interest: str = "0"
    timestamp: float = 0.0


class MarketDataCache:
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}
        self._tickers: dict[str, Ticker] = {}
        self._oracles: dict[str, float] = {}
        self._positions: dict[str, dict] = {}
        self._portfolio: dict | None = None

    def book(self, market: str) -> Book | None:
        return self._books.get(market)

    def ticker(self, market: str) -> Ticker | None:
        return self._tickers.get(market)

    def oracle_price(self, asset: str) -> float | None:
        return self._oracles.get(asset)

    def position(self, market: str) -> dict | None:
        return self._positions.get(market)

    def portfolio(self) -> dict | None:
        return self._portfolio

    def all_books(self) -> dict[str, Book]:
        return dict(self._books)

    def all_tickers(self) -> dict[str, Ticker]:
        return dict(self._tickers)

    def apply_book_snapshot(self, market: str, bids: list, asks: list) -> None:
        self._books[market] = Book(
            bids=sorted(bids, key=lambda x: float(x[0]), reverse=True),
            asks=sorted(asks, key=lambda x: float(x[0])),
            timestamp=time.time(),
        )

    def apply_book_delta(self, market: str, bids: list, asks: list) -> None:
        book = self._books.get(market)
        if book is None:
            self.apply_book_snapshot(market, bids, asks)
            return
        if bids:
            book.bids = _apply_levels(book.bids, bids, reverse=True)
        if asks:
            book.asks = _apply_levels(book.asks, asks, reverse=False)
        book.timestamp = time.time()

    def apply_ticker(self, market: str, data: dict) -> None:
        self._tickers[market] = Ticker(
            market=market,
            last_price=data.get("last_px", "0"),
            mark_price=data.get("mark_px", "0"),
            index_price=data.get("idx_px", "0"),
            best_bid=data.get("best_bid", "0"),
            best_ask=data.get("best_ask", "0"),
            volume_24h=data.get("vol_24h", "0"),
            change_24h=data.get("chg_24h", "0"),
            funding_rate=data.get("fund_rt", "0"),
            open_interest=data.get("oi", "0"),
            timestamp=time.time(),
        )

    def apply_oracle(self, asset: str, price: float) -> None:
        self._oracles[asset] = price

    def apply_position(self, market: str, data: dict) -> None:
        self._positions[market] = data

    def apply_portfolio(self, data: dict) -> None:
        self._portfolio = data

    def clear(self) -> None:
        self._books.clear()
        self._tickers.clear()
        self._oracles.clear()
        self._positions.clear()
        self._portfolio = None


def _apply_levels(
    existing: list[list[str]], deltas: list[list[str]], reverse: bool
) -> list[list[str]]:
    price_map: dict[str, str] = {lvl[0]: lvl[1] for lvl in existing}
    for delta in deltas:
        px, sz = delta[0], delta[1]
        if sz == "0" or float(sz) == 0:
            price_map.pop(px, None)
        else:
            price_map[px] = sz
    result = [[px, sz] for px, sz in price_map.items()]
    result.sort(key=lambda x: float(x[0]), reverse=reverse)
    return result
