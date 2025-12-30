import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from infrastructure.external.mexc_client.core import MEXCClient
from infrastructure.external.mexc_client.signer import generate_signature


def test_generate_signature_matches_helper():
    client = MEXCClient(api_key="dummy_key", secret_key="dummy_secret")
    params = {"b": 2, "a": 1}
    expected = generate_signature("dummy_secret", params)
    assert client._generate_signature(params) == expected


@pytest.mark.asyncio
async def test_place_market_order_delegates_to_create_order(monkeypatch):
    client = MEXCClient(api_key="dummy_key", secret_key="dummy_secret")
    captured = {}

    async def fake_create_order(**kwargs):
        captured.update(kwargs)
        return {"status": "ok"}

    monkeypatch.setattr(client, "create_order", fake_create_order)

    result = await client.place_market_order(symbol="QRLUSDT", side="buy", quantity=1.23)

    assert captured["symbol"] == "QRLUSDT"
    assert captured["side"] == "BUY"
    assert captured["order_type"] == "MARKET"
    assert captured["quantity"] == 1.23
    assert result == {"status": "ok"}


@pytest.mark.asyncio
async def test_place_market_order_requires_quantity(monkeypatch):
    client = MEXCClient(api_key="dummy_key", secret_key="dummy_secret")

    with pytest.raises(ValueError):
        await client.place_market_order(symbol="QRLUSDT", side="buy")


@pytest.mark.asyncio
async def test_listen_key_helpers_call_expected_endpoints(monkeypatch):
    client = MEXCClient(api_key="dummy_key", secret_key="dummy_secret")
    calls = []

    async def fake_request(method, endpoint, params=None, signed=False, max_retries=3):
        calls.append((method, endpoint, params, signed, max_retries))
        return {"ok": True}

    monkeypatch.setattr(client, "_request", fake_request)

    await client.create_listen_key()
    await client.keepalive_listen_key("abc")
    await client.get_listen_keys()
    await client.close_listen_key("abc")

    assert calls[0][:2] == ("POST", "/api/v3/userDataStream")
    assert calls[1][:3] == ("PUT", "/api/v3/userDataStream", {"listenKey": "abc"})
    assert calls[2][:2] == ("GET", "/api/v3/userDataStream")
    assert calls[3][:3] == ("DELETE", "/api/v3/userDataStream", {"listenKey": "abc"})
    assert all(call[3] for call in calls)
