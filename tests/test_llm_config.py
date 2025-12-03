"""
Tests for LLM provider configuration module.

Tests validate:
- Environment variable loading and defaults
- Provider selection (ollama, openrouter)
- Configuration validation
- Provider info retrieval
"""

import pytest
from unittest.mock import patch


class TestLLMConfigConstants:
    """Test module-level constants and defaults."""

    def test_valid_providers_contains_ollama(self):
        from app.config import VALID_PROVIDERS

        assert "ollama" in VALID_PROVIDERS

    def test_valid_providers_contains_openrouter(self):
        from app.config import VALID_PROVIDERS

        assert "openrouter" in VALID_PROVIDERS

    def test_default_provider_is_ollama(self):
        from app.config import DEFAULT_PROVIDER

        assert DEFAULT_PROVIDER == "ollama"

    def test_default_temperature(self):
        from app.config import DEFAULT_TEMPERATURE

        assert DEFAULT_TEMPERATURE == 0.7

    def test_default_timeout(self):
        from app.config import DEFAULT_TIMEOUT

        assert DEFAULT_TIMEOUT == 30


class TestValidateLLMConfig:
    """Test configuration validation."""

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "qwen3:8b",
            "OLLAMA_HOST": "http://localhost:11434",
        },
        clear=True,
    )
    def test_valid_ollama_config_passes(self):
        from app.config import validate_llm_config

        validate_llm_config()

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "openai/gpt-4",
            "OPENROUTER_API_KEY": "sk-test-key",
        },
        clear=True,
    )
    def test_valid_openrouter_config_passes(self):
        from app.config import validate_llm_config

        validate_llm_config()

    @patch.dict("os.environ", {"LLM_PROVIDER": "invalid_provider", "LLM_MODEL": "test"}, clear=True)
    def test_invalid_provider_raises_error(self):
        from app.config import ConfigurationError, validate_llm_config

        with pytest.raises(ConfigurationError) as exc_info:
            validate_llm_config()

        assert "invalid_provider" in str(exc_info.value)
        assert "ollama" in str(exc_info.value)
        assert "openrouter" in str(exc_info.value)

    @patch.dict("os.environ", {"LLM_PROVIDER": "ollama", "LLM_MODEL": ""}, clear=True)
    def test_empty_model_raises_error(self):
        from app.config import ConfigurationError, validate_llm_config

        with pytest.raises(ConfigurationError) as exc_info:
            validate_llm_config()

        assert "LLM_MODEL" in str(exc_info.value)

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "openai/gpt-4",
            "OPENROUTER_API_KEY": "",
        },
        clear=True,
    )
    def test_openrouter_without_api_key_raises_error(self):
        from app.config import ConfigurationError, validate_llm_config

        with pytest.raises(ConfigurationError) as exc_info:
            validate_llm_config()

        assert "OPENROUTER_API_KEY" in str(exc_info.value)

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "test",
            "LLM_TEMPERATURE": "-0.5",
        },
        clear=True,
    )
    def test_negative_temperature_raises_error(self):
        from app.config import ConfigurationError, validate_llm_config

        with pytest.raises(ConfigurationError) as exc_info:
            validate_llm_config()

        assert "LLM_TEMPERATURE" in str(exc_info.value)

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "test",
            "LLM_TEMPERATURE": "2.5",
        },
        clear=True,
    )
    def test_temperature_over_2_raises_error(self):
        from app.config import ConfigurationError, validate_llm_config

        with pytest.raises(ConfigurationError) as exc_info:
            validate_llm_config()

        assert "LLM_TEMPERATURE" in str(exc_info.value)

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "test",
            "LLM_TIMEOUT": "0",
        },
        clear=True,
    )
    def test_zero_timeout_raises_error(self):
        from app.config import ConfigurationError, validate_llm_config

        with pytest.raises(ConfigurationError) as exc_info:
            validate_llm_config()

        assert "LLM_TIMEOUT" in str(exc_info.value)

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "test",
            "LLM_TIMEOUT": "-10",
        },
        clear=True,
    )
    def test_negative_timeout_raises_error(self):
        from app.config import ConfigurationError, validate_llm_config

        with pytest.raises(ConfigurationError) as exc_info:
            validate_llm_config()

        assert "LLM_TIMEOUT" in str(exc_info.value)


class TestGetProviderInfo:
    """Test provider info retrieval."""

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "qwen3:8b",
            "OLLAMA_HOST": "http://localhost:11434",
            "LLM_TEMPERATURE": "0.5",
            "LLM_TIMEOUT": "60",
        },
        clear=True,
    )
    def test_ollama_provider_info(self):
        from app.config import get_provider_info

        info = get_provider_info()

        assert info["provider"] == "ollama"
        assert info["model"] == "qwen3:8b"
        assert info["host"] == "http://localhost:11434"
        assert info["temperature"] == 0.5
        assert info["timeout"] == 60

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "openai/gpt-4",
            "OPENROUTER_API_KEY": "sk-test",
            "OPENROUTER_BASE_URL": "https://custom.openrouter.ai",
            "LLM_TEMPERATURE": "0.8",
            "LLM_TIMEOUT": "45",
        },
        clear=True,
    )
    def test_openrouter_provider_info(self):
        from app.config import get_provider_info

        info = get_provider_info()

        assert info["provider"] == "openrouter"
        assert info["model"] == "openai/gpt-4"
        assert info["host"] == "https://custom.openrouter.ai"
        assert info["temperature"] == 0.8
        assert info["timeout"] == 45

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "test",
            "OPENROUTER_API_KEY": "sk-test",
        },
        clear=True,
    )
    def test_openrouter_without_base_url_returns_none_host(self):
        from app.config import get_provider_info

        info = get_provider_info()

        assert info["host"] is None


class TestGetLLMConfig:
    """Test getting the full LLM configuration object."""

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "llama3:8b",
            "OLLAMA_HOST": "http://localhost:11434",
            "LLM_TEMPERATURE": "0.7",
            "LLM_TIMEOUT": "30",
        },
        clear=True,
    )
    def test_get_llm_config_returns_config_object(self):
        from app.config import LLMConfig, get_llm_config

        config = get_llm_config()

        assert isinstance(config, LLMConfig)
        assert config.provider == "ollama"
        assert config.model == "llama3:8b"
        assert config.ollama_host == "http://localhost:11434"
        assert config.temperature == 0.7
        assert config.timeout == 30

    @patch.dict(
        "os.environ",
        {
            "LLM_PROVIDER": "openrouter",
            "LLM_MODEL": "anthropic/claude-3",
            "OPENROUTER_API_KEY": "sk-test-key",
            "OPENROUTER_BASE_URL": "https://api.openrouter.ai",
        },
        clear=True,
    )
    def test_get_llm_config_openrouter(self):
        from app.config import get_llm_config

        config = get_llm_config()

        assert config.provider == "openrouter"
        assert config.model == "anthropic/claude-3"
        assert config.openrouter_api_key == "sk-test-key"
        assert config.openrouter_base_url == "https://api.openrouter.ai"


class TestLLMConfigDefaults:
    """Test default values when env vars are not set."""

    @patch.dict("os.environ", {}, clear=True)
    def test_defaults_applied_when_no_env_vars(self):
        from app.config import get_llm_config

        config = get_llm_config()

        assert config.provider == "ollama"
        assert config.model == "qwen3:8b"
        assert config.ollama_host == "http://localhost:11434"
        assert config.temperature == 0.7
        assert config.timeout == 30
