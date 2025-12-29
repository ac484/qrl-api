"""Data collection phase."""
from typing import Any, Dict, Optional

from infrastructure.bot.bot_utils import compute_cost_metrics
from infrastructure.config.config import config


async def phase_data_collection(bot) -> Optional[Dict[str, Any]]:
    bot._log("Phase 2: Data Collection")
    try:
        ticker = await bot.mexc.get_ticker_24hr(bot.symbol)
        price = float(ticker.get("lastPrice", 0))
        volume_24h = float(ticker.get("volume", 0))
        price_change_pct = float(ticker.get("priceChangePercent", 0))
        bot._log(f"Price: {price}, Volume 24h: {volume_24h}, Change: {price_change_pct}%")
        await bot.redis.set_latest_price(price, volume_24h)
        await bot.redis.add_price_to_history(price)
        price_history = await bot.redis.get_price_history(limit=config.MA_LONG_PERIOD)

        qrl_balance = 0
        usdt_balance = 0
        if config.MEXC_API_KEY and config.MEXC_SECRET_KEY:
            try:
                account_info = await bot.mexc.get_account_info()
                for balance in account_info.get("balances", []):
                    asset = balance.get("asset")
                    if asset == "QRL":
                        qrl_balance = float(balance.get("free", 0))
                    elif asset == "USDT":
                        usdt_balance = float(balance.get("free", 0))
                bot._log(f"Balance: {qrl_balance} QRL, {usdt_balance} USDT")
                position_data = {"qrl_balance": str(qrl_balance), "usdt_balance": str(usdt_balance)}
                await bot.redis.set_position(position_data)

                cost_data = await bot.redis.get_cost_data()
                avg_cost_value = cost_data.get("avg_cost") if cost_data else None
                cost_metrics = compute_cost_metrics(price, qrl_balance, avg_cost_value)
                await bot.redis.set_cost_data(**cost_metrics)
            except Exception as e:  # pragma: no cover - downstream I/O
                bot._log(f"Failed to get account balance: {e}", "warning")

        return {
            "price": price,
            "volume_24h": volume_24h,
            "price_change_pct": price_change_pct,
            "price_history": price_history,
            "qrl_balance": qrl_balance,
            "usdt_balance": usdt_balance,
        }
    except Exception as e:
        bot._log(f"Data collection error: {e}", "error")
        return None
