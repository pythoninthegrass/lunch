"""
Application configuration module.

Supports multiple LLM providers (ollama, openrouter) via environment variables.
Based on django_ai_agent/core/config.py pattern, adapted for non-Django use.

Environment Variables:
    DEV: Development mode flag (default: False)

    LLM_PROVIDER: Provider type ("ollama" or "openrouter", default: "ollama")
    LLM_MODEL: Model name (default: "qwen3:8b")
    LLM_TEMPERATURE: Temperature for responses (default: 0.7, range: 0-2)
    LLM_TIMEOUT: Request timeout in seconds (default: 30)
    OLLAMA_HOST: Ollama server URL (default: "http://localhost:11434")
    OPENROUTER_API_KEY: API key for OpenRouter (required if using openrouter)
    OPENROUTER_BASE_URL: Custom OpenRouter base URL (optional)
"""

from dataclasses import dataclass
from decouple import config
from typing import Literal

# Application config
DEV = config("DEV", default=False, cast=bool)

# Type definitions
ProviderType = Literal["ollama", "openrouter"]

# LLM module-level constants
VALID_PROVIDERS: tuple[str, ...] = ("ollama", "openrouter")
DEFAULT_PROVIDER: ProviderType = "ollama"
DEFAULT_MODEL: str = "qwen3:8b"
DEFAULT_OLLAMA_HOST: str = "http://localhost:11434"
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_TIMEOUT: int = 30


class ConfigurationError(Exception):
    """Raised when LLM configuration is invalid."""

    pass


@dataclass
class LLMConfig:
    """LLM configuration data class."""

    provider: ProviderType
    model: str
    temperature: float
    timeout: int
    ollama_host: str | None = None
    openrouter_api_key: str | None = None
    openrouter_base_url: str | None = None


def get_llm_config() -> LLMConfig:
    """
    Load and return LLM configuration from environment variables.

    Returns:
        LLMConfig: Configuration object with all LLM settings.
    """
    provider = config("LLM_PROVIDER", default=DEFAULT_PROVIDER)
    model = config("LLM_MODEL", default=DEFAULT_MODEL)
    temperature = config("LLM_TEMPERATURE", default=DEFAULT_TEMPERATURE, cast=float)
    timeout = config("LLM_TIMEOUT", default=DEFAULT_TIMEOUT, cast=int)
    ollama_host = config("OLLAMA_HOST", default=DEFAULT_OLLAMA_HOST)
    openrouter_api_key = config("OPENROUTER_API_KEY", default="")
    openrouter_base_url = config("OPENROUTER_BASE_URL", default="")

    return LLMConfig(
        provider=provider,
        model=model,
        temperature=temperature,
        timeout=timeout,
        ollama_host=ollama_host if provider == "ollama" else None,
        openrouter_api_key=openrouter_api_key if openrouter_api_key else None,
        openrouter_base_url=openrouter_base_url if openrouter_base_url else None,
    )


def validate_llm_config() -> None:
    """
    Validate LLM configuration.

    Raises:
        ConfigurationError:
            - When LLM_PROVIDER is invalid
            - When required credentials are missing for selected provider
            - When temperature or timeout values are out of range
    """
    cfg = get_llm_config()

    if cfg.provider not in VALID_PROVIDERS:
        raise ConfigurationError(f"Invalid LLM_PROVIDER '{cfg.provider}'. Valid options: {', '.join(VALID_PROVIDERS)}")

    if not cfg.model:
        raise ConfigurationError("LLM_MODEL is required")

    if cfg.provider == "openrouter" and not cfg.openrouter_api_key:
        raise ConfigurationError("OPENROUTER_API_KEY required when LLM_PROVIDER=openrouter")

    if cfg.temperature < 0:
        raise ConfigurationError(f"LLM_TEMPERATURE must be >= 0, got {cfg.temperature}")

    if cfg.temperature > 2:
        raise ConfigurationError(f"LLM_TEMPERATURE must be <= 2, got {cfg.temperature}")

    if cfg.timeout <= 0:
        raise ConfigurationError(f"LLM_TIMEOUT must be positive, got {cfg.timeout}")


def get_provider_info() -> dict:
    """
    Get information about the currently configured provider.

    Useful for logging, debugging, and health check endpoints.

    Returns:
        dict: Provider information including provider, model, host, temperature, timeout
    """
    cfg = get_llm_config()

    info = {
        "provider": cfg.provider,
        "model": cfg.model,
        "temperature": cfg.temperature,
        "timeout": cfg.timeout,
    }

    if cfg.provider == "ollama":
        info["host"] = cfg.ollama_host
    elif cfg.provider == "openrouter":
        info["host"] = cfg.openrouter_base_url if cfg.openrouter_base_url else None
    else:
        info["host"] = None

    return info
