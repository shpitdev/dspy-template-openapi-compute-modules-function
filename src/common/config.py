"""Configuration helpers for DSPy LM setup."""

from __future__ import annotations

import json
from typing import Dict, Optional

import dspy
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_OPENROUTER_BASE = "https://openrouter.ai/api/v1"


class EnvironmentSettings(BaseSettings):
    """Project-wide environment settings loaded via pydantic-settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    model_name: str = Field(DEFAULT_MODEL, alias="DSPY_MODEL_NAME")
    dspy_api_key: Optional[str] = Field(None, alias="DSPY_API_KEY")
    openrouter_api_key: Optional[str] = Field(None, alias="OPENROUTER_API_KEY")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    dspy_api_base: Optional[str] = Field(None, alias="DSPY_API_BASE")
    openrouter_api_base: Optional[str] = Field(None, alias="OPENROUTER_API_BASE")
    raw_http_headers: Optional[str] = Field(None, alias="DSPY_HTTP_HEADERS")
    openrouter_http_referer: Optional[str] = Field(None, alias="OPENROUTER_HTTP_REFERER")
    openrouter_app_title: Optional[str] = Field(None, alias="OPENROUTER_APP_TITLE")


class LLMConfig(BaseModel):
    """Runtime configuration for the underlying language model."""

    model: str = DEFAULT_MODEL
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)

    @property
    def is_openrouter(self) -> bool:
        base = (self.api_base or "").lower()
        return "openrouter" in base


def _load_extra_headers(env: EnvironmentSettings) -> Dict[str, str]:
    """Build extra headers from env (JSON or individual fields)."""

    headers: Dict[str, str] = {}

    if env.raw_http_headers:
        try:
            headers.update(json.loads(env.raw_http_headers))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON in DSPY_HTTP_HEADERS environment variable") from exc

    if env.openrouter_http_referer:
        headers.setdefault("HTTP-Referer", env.openrouter_http_referer)

    if env.openrouter_app_title:
        headers.setdefault("X-Title", env.openrouter_app_title)

    return headers


def load_llm_config() -> LLMConfig:
    """Load LM configuration from environment variables."""

    env = EnvironmentSettings()

    api_key = env.dspy_api_key or env.openrouter_api_key or env.openai_api_key
    if not api_key:
        raise RuntimeError("No API key found. Set OPENROUTER_API_KEY, OPENAI_API_KEY, or DSPY_API_KEY.")

    api_base = env.dspy_api_base or env.openrouter_api_base
    if not api_base and env.openrouter_api_key:
        api_base = DEFAULT_OPENROUTER_BASE

    return LLMConfig(
        model=env.model_name or DEFAULT_MODEL,
        api_key=api_key,
        api_base=api_base,
        headers=_load_extra_headers(env),
    )


def configure_lm() -> dspy.LM:
    """Configure DSPy with the loaded LM settings and return the LM instance."""

    cfg = load_llm_config()
    lm = dspy.LM(
        cfg.model,
        api_key=cfg.api_key,
        api_base=cfg.api_base,
        headers=cfg.headers or None,
    )
    dspy.configure(lm=lm)
    return lm


__all__ = ["LLMConfig", "configure_lm", "load_llm_config", "DEFAULT_MODEL"]
