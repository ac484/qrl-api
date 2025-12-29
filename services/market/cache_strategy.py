"""Cache strategy helpers for market responses."""
from datetime import datetime


class CacheStrategy:
    @staticmethod
    def wrap(source: str, data):
        return {"source": source, "data": data, "timestamp": datetime.now().isoformat()}
