import logging

from app.llm.logging_config import (
    configure_llm_logger,
    get_llm_log_level,
    should_log_llm_prompts,
    should_log_llm_responses,
)


def test_llm_log_level_defaults_to_info(monkeypatch):
    monkeypatch.delenv("LLM_LOG_LEVEL", raising=False)

    assert get_llm_log_level() == logging.INFO


def test_llm_log_level_uses_env_value(monkeypatch):
    monkeypatch.setenv("LLM_LOG_LEVEL", "DEBUG")

    assert get_llm_log_level() == logging.DEBUG


def test_llm_log_level_invalid_value_falls_back_to_info(monkeypatch):
    monkeypatch.setenv("LLM_LOG_LEVEL", "NOT_A_LEVEL")

    assert get_llm_log_level() == logging.INFO


def test_prompt_response_flags_default_false(monkeypatch):
    monkeypatch.delenv("LLM_LOG_PROMPT", raising=False)
    monkeypatch.delenv("LLM_LOG_RESPONSE", raising=False)

    assert should_log_llm_prompts() is False
    assert should_log_llm_responses() is False


def test_prompt_response_flags_use_env_values(monkeypatch):
    monkeypatch.setenv("LLM_LOG_PROMPT", "true")
    monkeypatch.setenv("LLM_LOG_RESPONSE", "1")

    assert should_log_llm_prompts() is True
    assert should_log_llm_responses() is True


def test_configure_llm_logger_applies_env_level(monkeypatch):
    monkeypatch.setenv("LLM_LOG_LEVEL", "ERROR")

    logger = configure_llm_logger("app.llm.test")

    assert logger.level == logging.ERROR
