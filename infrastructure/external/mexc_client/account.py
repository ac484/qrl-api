"""
Account and balance helpers extracted from MEXC client core.
"""
from typing import Any, Dict, Optional

from infrastructure.utils.type_safety import safe_float


def build_balance_map(account_info: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    balances: Dict[str, Dict[str, str]] = {}
    for balance in account_info.get("balances", []):
        asset = balance.get("asset")
        if not asset:
            continue
        balances[asset] = {
            "free": balance.get("free", "0"),
            "locked": balance.get("locked", "0"),
            "total": safe_float(balance.get("free", 0))
            + safe_float(balance.get("locked", 0)),
        }
    return balances


async def fetch_balance_snapshot(client: "MEXCClient", symbol: str = "QRLUSDT") -> Dict[str, Any]:
    """Fetch balances with accompanying price data."""
    account_info = await client.get_account_info()
    ticker = await client.get_ticker_price(symbol)
    price = safe_float(ticker.get("price"))
    balances = build_balance_map(account_info)

    qrl_balance = balances.get("QRL", {"free": "0", "locked": "0", "total": 0})
    usdt_balance = balances.get("USDT", {"free": "0", "locked": "0", "total": 0})

    qrl_total = safe_float(qrl_balance.get("total", 0))
    qrl_value_usdt = qrl_total * price

    return {
        "balances": {
            "QRL": {**qrl_balance, "price": price, "value_usdt": qrl_value_usdt},
            "USDT": usdt_balance,
        },
        "raw": account_info,
        "price": {symbol: price},
    }

__all__ = ["build_balance_map", "fetch_balance_snapshot"]
