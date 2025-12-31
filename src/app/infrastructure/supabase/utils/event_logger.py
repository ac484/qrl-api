"""
Simple event logger that writes structured events to Supabase when available.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from src.app.infrastructure.supabase.client import supabase_client

logger = logging.getLogger(__name__)


class EventLogger:
    def __init__(self, table_name: str = "event_logs") -> None:
        self.table_name = table_name

    def log(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Persist an event to Supabase if configured; otherwise fall back to app logs.
        """
        client = supabase_client.get_client()
        event = {
            "event_type": event_type,
            "payload": payload,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if client is None:
            logger.info("Supabase not configured; logging event locally: %s", event)
            return False

        client.table(self.table_name).insert(event).execute()
        return True


__all__ = ["EventLogger"]
