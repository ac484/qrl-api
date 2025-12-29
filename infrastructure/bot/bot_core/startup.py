"""Startup and validation phase."""

async def phase_startup(bot) -> bool:
    bot._log("Phase 1: Startup & Validation")
    if not bot.redis.connected:
        bot._log("Redis not connected", "error")
        return False
    position = await bot.redis.get_position()
    bot._log(f"Current position loaded: {len(position)} fields")
    layers = await bot.redis.get_position_layers()
    if layers:
        bot._log(f"Position layers: core={layers.get('core_qrl', '0')} QRL")
    return True
