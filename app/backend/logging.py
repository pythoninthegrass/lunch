"""
Structured logging module using Eliot.

Provides ISO-timestamped, causal logging for business logic operations.
"""

import json
import sys
from datetime import UTC, datetime, timezone
from eliot import add_destinations, log_call, start_action, start_task
from typing import Any


def _format_message(message: dict[str, Any]) -> str:
    """Format eliot message with ISO timestamp to stderr."""
    timestamp = datetime.now(UTC).isoformat()
    action_type = message.get("action_type", message.get("message_type", "unknown"))
    action_status = message.get("action_status", "")

    # Build a concise log line
    parts = [f"[{timestamp}]", action_type]
    if action_status:
        parts.append(f"({action_status})")

    # Add relevant fields (exclude eliot internals)
    skip_keys = {
        "action_type",
        "message_type",
        "action_status",
        "task_uuid",
        "task_level",
        "timestamp",
    }
    fields = {k: v for k, v in message.items() if k not in skip_keys}
    if fields:
        parts.append(json.dumps(fields, default=str))

    return " ".join(parts)


def _stderr_destination(message: dict[str, Any]) -> None:
    """Write formatted log message to stderr."""
    print(_format_message(message), file=sys.stderr, flush=True)


_logging_initialized = False


def setup_logging() -> None:
    """Initialize eliot logging to stderr with ISO timestamps. Idempotent."""
    global _logging_initialized
    if _logging_initialized:
        return
    _logging_initialized = True
    add_destinations(_stderr_destination)


# Export commonly used eliot functions
__all__ = ["setup_logging", "start_action", "start_task", "log_call"]
