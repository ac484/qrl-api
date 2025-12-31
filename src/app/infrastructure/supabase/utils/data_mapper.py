"""
Helpers for mapping between DTOs and Supabase records.
"""
from typing import Any, Dict, Mapping


class DataMapper:
    @staticmethod
    def to_db(record: Mapping[str, Any]) -> Dict[str, Any]:
        """Convert an inbound mapping into a plain dictionary for persistence."""
        return dict(record)

    @staticmethod
    def from_db(record: Mapping[str, Any]) -> Dict[str, Any]:
        """Convert a database record into a DTO-friendly dict."""
        return dict(record)


__all__ = ["DataMapper"]
