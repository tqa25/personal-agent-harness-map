from __future__ import annotations

from agent_harness.tools import get_current_time


def test_get_current_time_returns_utc_payload() -> None:
    result = get_current_time("UTC")

    assert result["timezone"] == "UTC"
    assert result["supported"] is True
    assert "iso8601" in result
    assert "unix_seconds" in result


def test_get_current_time_rejects_unsupported_timezone() -> None:
    result = get_current_time("Asia/Ho_Chi_Minh")

    assert result["timezone"] == "Asia/Ho_Chi_Minh"
    assert result["supported"] is False
    assert "error" in result
