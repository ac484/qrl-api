"""Strategy phase."""
from typing import Dict

from infrastructure.bot.bot_utils import derive_ma_pair
from infrastructure.config.config import config


async def phase_strategy(bot, market_data: Dict[str, float]) -> str:
    bot._log("Phase 3: Strategy Execution")
    price_history = market_data.get("price_history", [])
    ma_pair = derive_ma_pair(price_history, config.MA_SHORT_PERIOD, config.MA_LONG_PERIOD)
    if not ma_pair:
        bot._log("Insufficient price history for MA calculation", "warning")
        return "HOLD"
    short_ma, long_ma = ma_pair
    bot._log(f"MA Short: {short_ma:.5f}, MA Long: {long_ma:.5f}")
    if short_ma > long_ma * (1 + config.SIGNAL_THRESHOLD):
        return "BUY"
    if short_ma < long_ma * (1 - config.SIGNAL_THRESHOLD):
        return "SELL"
    return "HOLD"
