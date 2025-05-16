import uuid
from datetime import datetime, timezone

from src.agents.side_effects_interceptor import _safe_uuid4, _safe_time


def time_iso() -> str:
    """Returns the current time in ISO 8601 format."""
    return datetime.fromtimestamp(_safe_time(timezone.utc)).isoformat()


def gen_trace_id() -> str:
    """Generates a new trace ID."""
    return f"trace_{_safe_uuid4().hex}"


def gen_span_id() -> str:
    """Generates a new span ID."""
    return f"span_{_safe_uuid4().hex[:24]}"


def gen_group_id() -> str:
    """Generates a new group ID."""
    return f"group_{_safe_uuid4().hex[:24]}"
