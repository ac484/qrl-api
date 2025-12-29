"""Execution phase."""
from infrastructure.config.config import config


async def phase_execution(bot, signal: str, market_data, risk_check):
    bot._log("Phase 5: Execution")
    price = market_data.get("price", 0)
    quantity = config.BASE_ORDER_USDT / price if signal == "BUY" else market_data.get("qrl_balance", 0)
    if quantity <= 0:
        return {"success": False, "message": "Quantity is zero"}
    if bot.dry_run:
        bot._log(f"DRY RUN: {signal} {quantity} QRL at {price}")
        return {"success": True, "dry_run": True, "quantity": quantity, "price": price}
    order = await bot.mexc.place_market_order(symbol=bot.symbol, side=signal, quantity=quantity)
    bot._log(f"Order executed: {order}")
    return {"success": True, "order": order, "quantity": quantity, "price": price}
