from __future__ import annotations
from datetime import datetime, timezone
import uuid

ALLOWED_TASK_STATUS = {"OPEN", "IN_PROGRESS", "COMPLETE"}

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"

def generate_unique_id(prefix: str, existing_ids: set) -> str:
    while True:
        candidate = f"{prefix}_{uuid.uuid4().hex[:12]}"
        if candidate not in existing_ids:
            return candidate