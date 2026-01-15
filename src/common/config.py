"""Configuration helpers for DSPy LM setup."""

from __future__ import annotations

import json
import os
from pathlib import Path

import dspy
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"
DEFAULT_LOCAL_MODEL = "Nemotron-3-Nano-30B-A3B-UD-Q3_K_XL.gguf"
DEFAULT_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
DEFAULT_LOCAL_BASE = "http://localhost:8080/v1"
DEFAULT_CACHE_DIR = Path("data/.dspy_cache")


class EnvironmentSettings(BaseSettings):
    """Project-wide environment settings loaded via pydantic-settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    provider: str = Field("openrouter", alias="DSPY_PROVIDER")
    model_name: str | None = Field(None, alias="DSPY_MODEL_NAME")
    openrouter_api_key: str | None = Field(None, alias="OPENROUTER_API_KEY")
    local_base: str | None = Field(None, alias="DSPY_LOCAL_BASE")
    raw_http_headers: str | None = Field(None, alias="DSPY_HTTP_HEADERS")
    openrouter_http_referer: str | None = Field(None, alias="OPENROUTER_HTTP_REFERER")
    openrouter_app_title: str | None = Field(None, alias="OPENROUTER_APP_TITLE")


class LLMConfig(BaseModel):
    """Runtime configuration for the underlying language model."""

    model: str = DEFAULT_MODEL
    api_key: str | None = None
    api_base: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)

    @property
    def is_openrouter(self) -> bool:
        base = (self.api_base or "").lower()
        return "openrouter" in base

    @property
    def is_local(self) -> bool:
        return self.api_key == "dummy" or self.api_key is None


def _load_extra_headers(env: EnvironmentSettings) -> dict[str, str]:
    """Build extra headers from env (JSON or individual fields)."""

    headers: dict[str, str] = {}

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

    env = EnvironmentSettings()  # pyright: ignore[reportCallIssue]
    provider = env.provider.lower()

    if provider == "local":
        model_name = env.model_name or DEFAULT_LOCAL_MODEL
        # LiteLLM requires openai/ prefix for OpenAI-compatible local servers
        if not model_name.startswith("openai/"):
            model_name = f"openai/{model_name}"
        return LLMConfig(
            model=model_name,
            api_key="dummy",  # LiteLLM requires a non-None api_key for openai provider
            api_base=env.local_base or DEFAULT_LOCAL_BASE,
            headers={},
        )

    # OpenRouter provider (default)
    if not env.openrouter_api_key:
        raise RuntimeError("No API key found. Set OPENROUTER_API_KEY or use DSPY_PROVIDER=local.")

    model_name = env.model_name or DEFAULT_MODEL
    # Ensure model has openrouter/ prefix for litellm provider routing
    if not model_name.startswith("openrouter/"):
        model_name = f"openrouter/{model_name}"

    return LLMConfig(
        model=model_name,
        api_key=env.openrouter_api_key,
        api_base=DEFAULT_OPENROUTER_BASE,
        headers=_load_extra_headers(env),
    )


def get_display_model_name(model: str | None = None) -> str | None:
    """Strip LiteLLM provider routing prefixes (openai/, openrouter/, etc.) for display/storage."""
    if model is None:
        model = dspy.settings.lm.model if dspy.settings.lm else None

    if model is None:
        return None

    prefixes = ("openai/", "openrouter/", "anthropic/", "azure/", "huggingface/")
    for prefix in prefixes:
        if model.startswith(prefix):
            return model[len(prefix) :]

    return model


def ensure_dspy_cache_dir(cache_dir: Path | None = None) -> Path:
    """Ensure DSPy cache directory exists and is configured."""
    path = cache_dir or DEFAULT_CACHE_DIR
    path.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DSPY_CACHEDIR", str(path))
    return path


def configure_lm() -> dspy.LM:
    ensure_dspy_cache_dir()
    cfg = load_llm_config()
    lm = dspy.LM(
        cfg.model,
        api_key=cfg.api_key,
        api_base=cfg.api_base,
        headers=cfg.headers or None,
        max_tokens=8000,
        cache=False,
    )
    dspy.configure(lm=lm)
    return lm


__all__ = [
    "DEFAULT_MODEL",
    "DEFAULT_CACHE_DIR",
    "LLMConfig",
    "configure_lm",
    "ensure_dspy_cache_dir",
    "get_display_model_name",
    "load_llm_config",
]
