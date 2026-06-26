from __future__ import annotations

import pytest

from agent_harness.autonomy import (
    ActionKind,
    AutonomyModeError,
    AutonomyConfig,
    AutonomySession,
    AutonomyLevel,
    DeliveryActionBlocked,
    handle_autonomy_command,
    parse_autonomy_level,
)


def test_default_autonomy_level_is_edit_and_allows_repository_edits() -> None:
    session = AutonomySession.default()
    config = AutonomyConfig()

    assert config.default_level is AutonomyLevel.EDIT
    assert session.level is AutonomyLevel.EDIT
    assert session.can_perform(ActionKind.REPOSITORY_EDIT) is True


def test_parse_and_change_supported_autonomy_levels() -> None:
    session = AutonomySession.default()

    assert parse_autonomy_level("edit") is AutonomyLevel.EDIT
    assert parse_autonomy_level("deliver") is AutonomyLevel.DELIVER
    assert parse_autonomy_level("auto") is AutonomyLevel.AUTO

    output = session.change_mode("deliver")
    assert session.level is AutonomyLevel.DELIVER
    assert "deliver" in output

    output = session.change_mode("auto")
    assert session.level is AutonomyLevel.AUTO
    assert "auto" in output
    assert "boundaries" in output.lower()


def test_invalid_autonomy_mode_raises_clear_error() -> None:
    with pytest.raises(AutonomyModeError, match="Invalid autonomy mode 'ship'"):
        parse_autonomy_level("ship")


def test_delivery_actions_are_gated_by_mode_or_explicit_approval() -> None:
    session = AutonomySession.default()

    assert session.can_perform(ActionKind.DELIVERY_ACTION) is False
    with pytest.raises(DeliveryActionBlocked, match="Delivery Actions require"):
        session.require_allowed(ActionKind.DELIVERY_ACTION)

    assert session.can_perform(
        ActionKind.DELIVERY_ACTION,
        explicit_approval=True,
    ) is True
    session.require_allowed(ActionKind.DELIVERY_ACTION, explicit_approval=True)

    session.change_mode("deliver")
    assert session.can_perform(ActionKind.DELIVERY_ACTION) is True

    session.change_mode("auto")
    assert session.can_perform(ActionKind.DELIVERY_ACTION) is True


def test_autonomy_command_inspects_and_changes_current_mode() -> None:
    session = AutonomySession.default()

    output = handle_autonomy_command(session, "/autonomy")
    assert "Current autonomy level: edit" in output

    output = handle_autonomy_command(session, "/autonomy deliver")
    assert session.level is AutonomyLevel.DELIVER
    assert "Current autonomy level: deliver" in output

    with pytest.raises(AutonomyModeError, match="Expected one of: edit, deliver, auto"):
        handle_autonomy_command(session, "/autonomy unknown")
