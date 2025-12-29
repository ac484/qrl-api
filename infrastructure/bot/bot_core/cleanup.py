"""Cleanup phase."""
from datetime import datetime


async def phase_cleanup(bot, result):
    bot._log("Phase 6: Cleanup & Reporting")
    result["completed_at"] = datetime.now().isoformat()
