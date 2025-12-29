"""Risk control phase."""
from typing import Dict


async def phase_risk_control(bot, signal: str, market_data: Dict[str, float]) -> Dict[str, str]:
    bot._log("Phase 4: Risk Control")
    if signal == "HOLD":
        return {"allowed": False, "reason": "No trading signal"}
    if signal == "BUY":
        usdt_balance = market_data.get("usdt_balance", 0)
        if usdt_balance <= 0:
            return {"allowed": False, "reason": "Insufficient USDT"}
    if signal == "SELL":
        qrl_balance = market_data.get("qrl_balance", 0)
        if qrl_balance <= 0:
            return {"allowed": False, "reason": "No QRL to sell"}
    return {"allowed": True, "reason": "Risk checks passed"}
