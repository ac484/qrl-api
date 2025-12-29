"""
Compatibility shim for TradingBot.
Delegates to infrastructure.bot.bot_core.TradingBot to match folder layout.
"""
from infrastructure.bot.bot_core import TradingBot

__all__ = ["TradingBot"]
