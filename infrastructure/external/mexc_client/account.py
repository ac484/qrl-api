"""
Account and balance helpers extracted from MEXC client core.
"""
from typing import Any, Dict

from infrastructure.utils.type_safety import safe_float


QRL_USDT_SYMBOL = "QRLUSDT"


def build_balance_map(account_info: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    balances: Dict[str, Dict[str, str]] = {}
    for balance in account_info.get("balances", []):
        asset = balance.get("asset")
        if asset not in {"QRL", "USDT"}:
            continue
        balances[asset] = {
            "free": balance.get("free", "0"),
            "locked": balance.get("locked", "0"),
            "total": safe_float(balance.get("free", 0))
            + safe_float(balance.get("locked", 0)),
        }
    return balances


async def fetch_balance_snapshot(client: "MEXCClient") -> Dict[str, Any]:
    """Fetch QRL/USDT spot balances with accompanying price data."""
    account_info = await client.get_account_info()
    ticker = await client.get_ticker_price(QRL_USDT_SYMBOL)
    if ticker.get("price") is None:
        raise ValueError("Missing QRL/USDT price from exchange")

    price = safe_float(ticker.get("price"))
    balances = build_balance_map(account_info)

    qrl_balance = balances.get("QRL") or {"free": "0", "locked": "0", "total": 0}
    usdt_balance = balances.get("USDT") or {"free": "0", "locked": "0", "total": 0}

    return {
        "balances": {
            "QRL": {**qrl_balance, "price": price},
            "USDT": usdt_balance,
        },
        "prices": {QRL_USDT_SYMBOL: price},
        "raw": account_info,
    }

__all__ = ["build_balance_map", "fetch_balance_snapshot"]
