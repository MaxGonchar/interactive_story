class DomainError(Exception):
    """Base for all domain-rule violations."""

    http_status: int = 409
    error_code: str = "domain_error"
    message: str = "A domain rule was violated"


class SceneFinishedError(DomainError):
    """Operation rejected because the scene is already finished."""

    error_code = "scene_finished"
    message = "Scene is already finished"


class NoAssistantMessageError(DomainError):
    """Regenerate rejected: last message is not from the assistant."""

    error_code = "no_assistant_message"
    message = "No assistant message to regenerate"


class NoUserMessageError(DomainError):
    """Regenerate rejected: no preceding user message found."""

    error_code = "no_user_message"
    message = "No preceding user message to regenerate from"


class NoStepsError(DomainError):
    """Choice operation rejected: story has no steps yet."""

    error_code = "no_steps"
    message = "Story has no steps yet"


class ActiveSceneExistsError(DomainError):
    """Scene creation rejected: story already has an active (unfinished) scene."""

    error_code = "active_scene_exists"
    message = "Story already has an active scene"


class NarratorModeNotSupportedError(DomainError):
    """Narrator mode is unavailable for this story type."""

    error_code = "narrator_mode_not_supported"
    message = "Narrator mode is only supported for scene stories"


class NotFoundError(DomainError):
    """Raised by repositories when a requested record does not exist."""

    http_status = 404
    error_code = "not_found"
    message = "Resource not found"

    def __init__(self, message: str = "Resource not found") -> None:
        self.message = message
        super().__init__(message)


class LLMError(Exception):
    """Raised when an LLM/upstream API call fails."""
