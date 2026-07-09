from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import defaultdict
from collections.abc import AsyncIterator
from typing import Any

import websockets
from websockets.asyncio.client import connect

from obsdn.auth import HmacSigner
from obsdn.ws.cache import MarketDataCache
from obsdn.ws.channel import Channel, ChannelName
from obsdn.ws.event import Event, EventType, Update

logger = logging.getLogger("obsdn.ws")

RECONNECT_DELAY = 1.0
PING_INTERVAL = 30
PING_TIMEOUT = 20


class Session:
    def __init__(
        self,
        ws_url: str,
        signer: HmacSigner | None = None,
        cache: MarketDataCache | None = None,
    ):
        self._ws_url = ws_url
        self._signer = signer
        self._cache = cache or MarketDataCache()
        self._ws: Any = None
        self._subscriptions: set[Channel] = set()
        self._queues: dict[Channel, list[asyncio.Queue]] = defaultdict(list)
        self._supervisor_task: asyncio.Task | None = None
        self._running = False
        self._authenticated = False

    @property
    def cache(self) -> MarketDataCache:
        return self._cache

    async def connect(self) -> None:
        self._running = True
        self._supervisor_task = asyncio.create_task(self._supervisor())

    async def subscribe(self, channel: Channel) -> AsyncIterator[Update]:
        q: asyncio.Queue[Update | None] = asyncio.Queue(maxsize=1024)
        self._queues[channel].append(q)
        if channel not in self._subscriptions:
            self._subscriptions.add(channel)
            if self._ws is not None:
                await self._send_sub(channel)
        return _QueueIterator(q)

    async def unsubscribe(self, channel: Channel) -> None:
        self._subscriptions.discard(channel)
        if self._ws is not None:
            try:
                await self._ws.send(
                    json.dumps(
                        {
                            "op": "unsub",
                            "channel": channel.name.value,
                            "params": channel.wire_params(),
                        }
                    )
                )
            except Exception:
                pass
        for q in self._queues.pop(channel, []):
            q.put_nowait(None)

    async def shutdown(self) -> None:
        self._running = False
        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass
        if self._supervisor_task is not None:
            self._supervisor_task.cancel()
            try:
                await self._supervisor_task
            except (asyncio.CancelledError, Exception):
                pass
        for queues in self._queues.values():
            for q in queues:
                q.put_nowait(None)

    async def _supervisor(self) -> None:
        while self._running:
            try:
                async with connect(
                    self._ws_url,
                    ping_interval=PING_INTERVAL,
                    ping_timeout=PING_TIMEOUT,
                ) as ws:
                    self._ws = ws
                    self._authenticated = False
                    if self._signer:
                        await self._authenticate()
                    for ch in list(self._subscriptions):
                        await self._send_sub(ch)
                    await self._read_loop(ws)
            except (
                websockets.ConnectionClosed,
                websockets.InvalidURI,
                OSError,
            ) as e:
                logger.warning("WS disconnected: %s, reconnecting in %.1fs", e, RECONNECT_DELAY)
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.error("WS unexpected error: %s", e)

            self._ws = None
            if self._running:
                self._dispatch_reconnected()
                await asyncio.sleep(RECONNECT_DELAY)

    async def _authenticate(self) -> None:
        if not self._signer:
            return
        ts = str(int(time.time()))
        sig = self._signer.sign_ws(ts)
        await self._ws.send(
            json.dumps(
                {
                    "op": "auth",
                    "params": {
                        "key": self._signer.api_key,
                        "timestamp": ts,
                        "signature": sig,
                    },
                }
            )
        )

    async def _send_sub(self, channel: Channel) -> None:
        if channel.name.is_private and not self._authenticated and self._signer:
            pass
        msg = {
            "op": "sub",
            "channel": channel.name.value,
        }
        params = channel.wire_params()
        if params:
            msg["params"] = params
        await self._ws.send(json.dumps(msg))

    async def _read_loop(self, ws: Any) -> None:
        async for raw in ws:
            try:
                frame = json.loads(raw)
            except json.JSONDecodeError:
                continue
            self._handle_frame(frame)

    def _handle_frame(self, frame: dict) -> None:
        # Server uses "type" not "op" as the frame discriminator
        op = frame.get("type", frame.get("op", ""))

        if op == "welcome":
            return

        if op == "auth":
            if frame.get("success"):
                self._authenticated = True
                logger.debug("WS authenticated")
            else:
                logger.warning("WS auth failed: %s", frame.get("message"))
                self._dispatch_event(
                    Event(
                        type=EventType.UNAUTHORIZED,
                        message=frame.get("message", "auth failed"),
                    )
                )
            return

        if op in ("error", "subscribed", "unsubscribed"):
            if op == "error":
                logger.warning("WS error: %s", frame.get("message"))
            return

        channel_str = frame.get("channel")
        if not channel_str:
            return

        try:
            ch_name = ChannelName(channel_str)
        except ValueError:
            return

        data = frame.get("data", {})
        gsn = frame.get("gsn", 0)
        ts = frame.get("ts")
        update_reason = frame.get("update_reason")
        # Filter comes in "filter" field or nested in "params"
        filt = frame.get("filter", {})
        filter_val = (
            filt.get("market", filt.get("asset", "")) if isinstance(filt, dict) else str(filt)
        )
        is_snapshot = op == "snapshot"

        self._apply_to_cache(ch_name, filter_val, data, is_snapshot)

        evt_type = EventType.SNAPSHOT if is_snapshot else EventType.UPDATE
        update = Update(
            channel=ch_name,
            filter=filter_val,
            gsn=gsn,
            data=data,
            event_type=evt_type,
            ts=ts,
            update_reason=update_reason,
        )
        self._dispatch_update(ch_name, filter_val, update)

    def _apply_to_cache(self, ch: ChannelName, filt: str, data: Any, is_snapshot: bool) -> None:
        if ch == ChannelName.BOOK:
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            checksum = data.get("checksum")
            if is_snapshot:
                self._cache.apply_book_snapshot(filt, bids, asks, checksum)
            else:
                self._cache.apply_book_delta(filt, bids, asks, checksum)
        elif ch == ChannelName.TICKER:
            self._cache.apply_ticker(filt, data)
        elif ch == ChannelName.ORACLE:
            price = data.get("px") or data.get("price")
            if price is not None:
                self._cache.apply_oracle(filt, float(price))
        elif ch == ChannelName.POSITION:
            self._cache.apply_position(filt, data)
        elif ch == ChannelName.PORTFOLIO:
            self._cache.apply_portfolio(data)

    def _dispatch_update(self, ch: ChannelName, filt: str, update: Update) -> None:
        for channel, queues in self._queues.items():
            if channel.name == ch and (not channel.filter or channel.filter == filt):
                for q in queues:
                    try:
                        q.put_nowait(update)
                    except asyncio.QueueFull:
                        pass

    def _dispatch_event(self, event: Event) -> None:
        for queues in self._queues.values():
            for q in queues:
                try:
                    q.put_nowait(event)
                except asyncio.QueueFull:
                    pass

    def _dispatch_reconnected(self) -> None:
        self._dispatch_event(Event(type=EventType.RECONNECTED))


class _QueueIterator:
    def __init__(self, q: asyncio.Queue):
        self._q = q

    def __aiter__(self) -> _QueueIterator:
        return self

    async def __anext__(self) -> Update:
        item = await self._q.get()
        if item is None:
            raise StopAsyncIteration
        return item
