from __future__ import annotations

from agent_harness.instructions import GENERAL_AGENT_INSTRUCTIONS


def test_instructions_cover_harness_behaviors() -> None:
    instructions = GENERAL_AGENT_INSTRUCTIONS.lower()

    assert "planning mode" in instructions
    assert "todos" in instructions
    assert "web search" in instructions
    assert "cite" in instructions
    assert "session memory" in instructions
