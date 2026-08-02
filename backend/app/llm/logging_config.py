import logging
import os

from langchain_core.messages import BaseMessage

_TRUE_VALUES = {"1", "true", "yes", "on"}
_DEFAULT_LOG_LEVEL = "INFO"


def _parse_bool_env(var_name: str, *, default: bool = False) -> bool:
    raw = os.getenv(var_name)
    if raw is None:
        return default
    return raw.strip().lower() in _TRUE_VALUES


def _parse_log_level(var_name: str, *, default: str = _DEFAULT_LOG_LEVEL) -> int:
    raw = os.getenv(var_name, default).strip().upper()
    parsed = logging.getLevelName(raw)
    if isinstance(parsed, int):
        return parsed
    return logging.getLevelName(default)


def get_llm_log_level() -> int:
    return _parse_log_level("LLM_LOG_LEVEL")


def should_log_llm_prompts() -> bool:
    return _parse_bool_env("LLM_LOG_PROMPT", default=False)


def should_log_llm_responses() -> bool:
    return _parse_bool_env("LLM_LOG_RESPONSE", default=False)


def configure_llm_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(get_llm_log_level())
    return logger


def log_prompt_messages(logger: logging.Logger, messages: list[BaseMessage]) -> None:
    if not should_log_llm_prompts():
        return

    level = get_llm_log_level()
    if not logger.isEnabledFor(level):
        return

    logger.log(level, "=== LLM PROMPT START ===")
    for message in messages:
        logger.log(level, "%s: %s", message.type.upper(), message.content)
    logger.log(level, "=== LLM PROMPT END ===")


def log_response_content(logger: logging.Logger, response_content: str) -> None:
    if not should_log_llm_responses():
        return

    level = get_llm_log_level()
    if not logger.isEnabledFor(level):
        return

    logger.log(level, "=== LLM RESPONSE START ===")
    logger.log(level, "%s", response_content)
    logger.log(level, "=== LLM RESPONSE END ===")
