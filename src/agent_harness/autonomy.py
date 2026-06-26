from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AutonomyLevel(str, Enum):
    EDIT = "edit"
    DELIVER = "deliver"
    AUTO = "auto"


class ActionKind(str, Enum):
    REPOSITORY_EDIT = "repository_edit"
    DELIVERY_ACTION = "delivery_action"


class AutonomyModeError(ValueError):
    """Raised when an unsupported autonomy mode is requested."""


class DeliveryActionBlocked(PermissionError):
    """Raised when the current autonomy level cannot perform a delivery action."""


DEFAULT_AUTO_BOUNDARIES = (
    "current repository",
    "current goal",
    "explicitly configured boundaries",
)


@dataclass(frozen=True)
class AutonomyConfig:
    default_level: AutonomyLevel = AutonomyLevel.EDIT
    auto_boundaries: tuple[str, ...] = DEFAULT_AUTO_BOUNDARIES


@dataclass
class AutonomySession:
    level: AutonomyLevel = AutonomyLevel.EDIT
    auto_boundaries: tuple[str, ...] = DEFAULT_AUTO_BOUNDARIES

    @classmethod
    def default(cls, config: AutonomyConfig | None = None) -> "AutonomySession":
        config = config or AutonomyConfig()
        return cls(level=config.default_level, auto_boundaries=config.auto_boundaries)

    def change_mode(self, mode: str | AutonomyLevel) -> str:
        self.level = parse_autonomy_level(mode)
        return self.status()

    def status(self) -> str:
        message = f"Current autonomy level: {self.level.value}"
        if self.level is AutonomyLevel.AUTO:
            boundaries = ", ".join(self.auto_boundaries)
            message = f"{message}. Auto mode boundaries: {boundaries}"
        return message

    def can_perform(
        self,
        action: ActionKind,
        *,
        explicit_approval: bool = False,
    ) -> bool:
        if action is ActionKind.REPOSITORY_EDIT:
            return True
        if action is ActionKind.DELIVERY_ACTION:
            return (
                explicit_approval
                or self.level in {AutonomyLevel.DELIVER, AutonomyLevel.AUTO}
            )
        return False

    def require_allowed(
        self,
        action: ActionKind,
        *,
        explicit_approval: bool = False,
    ) -> None:
        if self.can_perform(action, explicit_approval=explicit_approval):
            return
        if action is ActionKind.DELIVERY_ACTION:
            raise DeliveryActionBlocked(
                "Delivery Actions require deliver mode, auto mode, "
                "or explicit approval."
            )
        raise PermissionError(f"Action is not allowed: {action.value}")


def parse_autonomy_level(value: str | AutonomyLevel) -> AutonomyLevel:
    if isinstance(value, AutonomyLevel):
        return value

    normalized = value.strip().lower()
    for level in AutonomyLevel:
        if normalized == level.value:
            return level

    expected = ", ".join(level.value for level in AutonomyLevel)
    raise AutonomyModeError(
        f"Invalid autonomy mode '{value}'. Expected one of: {expected}."
    )


def handle_autonomy_command(session: AutonomySession, command: str) -> str:
    parts = command.split()
    if not parts or parts[0] != "/autonomy":
        raise AutonomyModeError("Autonomy commands must start with /autonomy.")
    if len(parts) == 1:
        return session.status()
    if len(parts) == 2:
        return session.change_mode(parts[1])
    raise AutonomyModeError("Usage: /autonomy [edit|deliver|auto]")
