from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated


def get_current_time(
    timezone: Annotated[
        str,
        "Timezone label requested by the user. Only 'UTC' is supported by this sample tool.",
    ] = "UTC",
) -> dict[str, object]:
    """Return the current UTC time as a simple sample tool."""
    if timezone.upper() != "UTC":
        return {
            "timezone": timezone,
            "supported": False,
            "error": "This sample tool only supports UTC.",
        }

    now = datetime.now(UTC)
    return {
        "timezone": "UTC",
        "supported": True,
        "iso8601": now.isoformat(),
        "unix_seconds": int(now.timestamp()),
    }


TOOLS = [get_current_time]
