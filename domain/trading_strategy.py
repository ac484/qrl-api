"""Basic trading strategy helpers."""
from typing import Iterable

from infrastructure.config.config import config


class TradingStrategy:
    """Simple moving-average crossover strategy."""

    def __init__(
        self,
        short_period: int | None = None,
        long_period: int | None = None,
    ):
        self.short_period = short_period or config.MA_SHORT_PERIOD
        self.long_period = long_period or config.MA_LONG_PERIOD

    def generate_signal(self, price_history: Iterable[float]) -> str:
        """Return BUY/SELL/HOLD based on moving average crossover."""
        prices = list(price_history)
        if len(prices) < self.long_period or self.long_period == 0:
            return "HOLD"

        short_slice = prices[-self.short_period :]
        long_slice = prices[-self.long_period :]

        if not short_slice or not long_slice:
            return "HOLD"

        short_ma = sum(short_slice) / len(short_slice)
        long_ma = sum(long_slice) / len(long_slice)

        if short_ma > long_ma:
            return "BUY"
        if short_ma < long_ma:
            return "SELL"
        return "HOLD"


__all__ = ["TradingStrategy"]
