import asyncio
import json
import sys
from pathlib import Path

import importlib

import pytest
from google.protobuf.struct_pb2 import Struct

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.app.infrastructure.external.mexc.ws import ws_client  # noqa: E402
from src.app.infrastructure.external.mexc.ws import ws_core  # noqa: E402


class FakeWebSocket:
    def __init__(self, incoming=None):
        self.incoming = asyncio.Queue()
        for item in incoming or []:
            self.incoming.put_nowait(item)
        self.sent = []
        self.closed = False

    async def send(self, data):
        self.sent.append(data)

    async def recv(self):
        return await self.incoming.get()

    async def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_client_subscribe_and_handle_ping(monkeypatch):
    fake_ws = FakeWebSocket(
        incoming=[json.dumps({"method": "PING"}), json.dumps({"channel": "ok"})]
    )

    async def fake_connect(*args, **kwargs):
        return fake_ws

    monkeypatch.setattr(ws_core.websockets, "connect", fake_connect)

    async with ws_client.MEXCWebSocketClient(
        subscriptions=["chan"], heartbeat=None
    ) as client:
        ping_message = await client.recv()
        data_message = await client.recv()

    assert json.loads(fake_ws.sent[0]) == {"method": "SUBSCRIPTION", "params": ["chan"]}
    assert json.loads(fake_ws.sent[1]) == {"method": "PONG"}
    assert ping_message == {"type": "ping"}
    assert data_message["channel"] == "ok"


@pytest.mark.asyncio
async def test_client_unsubscribe(monkeypatch):
    fake_ws = FakeWebSocket(incoming=[json.dumps({"channel": "ok"})])

    async def fake_connect(*args, **kwargs):
        return fake_ws

    monkeypatch.setattr(ws_core.websockets, "connect", fake_connect)

    async with ws_client.MEXCWebSocketClient(
        subscriptions=["spot@public.bookTicker"], heartbeat=None
    ) as client:
        await client.unsubscribe(["spot@public.bookTicker"])
        await client.recv()

    assert json.loads(fake_ws.sent[1]) == {
        "method": "UNSUBSCRIPTION",
        "params": ["spot@public.bookTicker"],
    }


@pytest.mark.asyncio
async def test_binary_decoder(monkeypatch):
    fake_ws = FakeWebSocket(incoming=[b"abc"])

    async def fake_connect(*args, **kwargs):
        return fake_ws

    monkeypatch.setattr(ws_core.websockets, "connect", fake_connect)

    async with ws_client.MEXCWebSocketClient(
        binary_decoder=lambda raw: {"decoded": raw.decode()}, heartbeat=None
    ) as client:
        message = await client.recv()

    assert message == {"decoded": "abc"}


@pytest.mark.asyncio
async def test_connect_public_trades_defaults_to_push_decoder(monkeypatch):
    captured = {}

    class DummyClient:
        def __init__(self, *args, **kwargs):
            captured["decoder"] = kwargs.get("binary_decoder")
            self._data = [{"ok": True}]

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        def __aiter__(self):
            return self

        async def __anext__(self):
            if not self._data:
                raise StopAsyncIteration
            return self._data.pop(0)

    monkeypatch.setattr(ws_client, "MEXCWebSocketClient", DummyClient)

    messages = []
    async for msg in ws_client.connect_public_trades("btc"):
        messages.append(msg)
        break

    assert captured["decoder"] is ws_client.decode_push_data
    assert messages[0]["ok"] is True


def test_channel_builders_and_proto_decoder():
    assert (
        ws_client.trade_stream("btcusdt")
        == "spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT"
    )
    assert ws_client.diff_depth_stream("qrlusdt", "10ms") == (
        "spot@public.aggre.depth.v3.api.pb@10ms@QRLUSDT"
    )
    assert ws_client.partial_depth_stream("qrlusdt", 10) == (
        "spot@public.limit.depth.v3.api.pb@QRLUSDT@10"
    )
    assert (
        ws_client.mini_tickers_stream("UTC+8")
        == "spot@public.miniTickers.v3.api.pb@UTC+8"
    )
    assert (
        ws_client.mini_ticker_stream("mxusdt", "UTC+8")
        == "spot@public.miniTicker.v3.api.pb@MXUSDT@UTC+8"
    )
    with pytest.raises(ValueError):
        ws_client.trade_stream("qrl", interval="1s")

    decoder = ws_client.build_protobuf_decoder(Struct)
    struct = Struct()
    struct.update({"foo": "bar"})
    decoded = decoder(struct.SerializeToString())
    assert decoded["foo"] == "bar"


def test_user_data_stream_builders():
    from src.app.infrastructure.external.mexc.websocket import data_streams
    from src.app.infrastructure.external.mexc.ws import ws_channels

    assert data_streams.account_update_stream() == "spot@private.account.v3.api.pb"
    assert data_streams.user_deals_stream() == "spot@private.deals.v3.api.pb"
    assert data_streams.user_orders_stream() == "spot@private.orders.v3.api.pb"
    assert data_streams.DEFAULT_USER_STREAM_CHANNELS == [
        "spot@private.account.v3.api.pb",
        "spot@private.deals.v3.api.pb",
        "spot@private.orders.v3.api.pb",
    ]
    # Legacy import path continues to work
    assert ws_channels.account_update_stream() == "spot@private.account.v3.api.pb"


def test_push_data_decoder_builds_from_generated_proto():
    from src.app.infrastructure.external.proto.websocket_pb import (
        PublicAggreDealsV3Api_pb2,
        PushDataV3ApiWrapper_pb2,
    )

    decoder = ws_client.decode_push_data
    payload = PushDataV3ApiWrapper_pb2.PushDataV3ApiWrapper(
        channel="spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT",
        publicAggreDeals=PublicAggreDealsV3Api_pb2.PublicAggreDealsV3Api(
            deals=[
                PublicAggreDealsV3Api_pb2.PublicAggreDealsV3ApiItem(
                    price="1.1", quantity="2.2", tradeType=1, time=123
                )
            ],
            eventType="aggTrade",
        ),
        symbol="BTCUSDT",
        sendTime=999,
    )

    decoded = decoder(payload.SerializeToString())

    assert decoded["channel"] == payload.channel
    assert decoded["publicAggreDeals"]["eventType"] == "aggTrade"
    assert decoded["publicAggreDeals"]["deals"][0]["price"] == "1.1"
