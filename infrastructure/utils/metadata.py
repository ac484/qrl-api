"""
Metadata helpers extracted from redis_helpers_core.
"""
from datetime import datetime
from typing import Any, Dict, Optional


def create_metadata(additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "stored_at": int(datetime.now().timestamp() * 1000),
    }
    if additional_data:
        metadata.update(additional_data)
    return metadata

__all__ = ["create_metadata"]
