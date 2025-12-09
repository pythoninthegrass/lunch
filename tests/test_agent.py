"""
Unit tests for AI agent module.
Tests agent functionality with mocked pydantic-ai components.
"""

import pytest
from app.config import LLMConfig
from unittest.mock import AsyncMock, Mock, patch


class TestCreateModelFromConfig:
    """Tests for create_model_from_config factory."""

    def test_creates_ollama_model(self):
        """Test creating Ollama model from config."""
        from app.backend.agent import create_model_from_config

        config = LLMConfig(
            provider="ollama",
            model="qwen3:8b",
            temperature=0.7,
            timeout=30,
            ollama_host="http://localhost:11434",
        )

        model = create_model_from_config(config)
        assert model is not None

    def test_creates_openrouter_model(self):
        """Test creating OpenRouter model from config."""
        from app.backend.agent import create_model_from_config

        config = LLMConfig(
            provider="openrouter",
            model="anthropic/claude-3.5-sonnet",
            temperature=0.7,
            timeout=30,
            openrouter_api_key="test-key",
        )

        model = create_model_from_config(config)
        assert model is not None

    def test_raises_for_unsupported_provider(self):
        """Test error for unsupported provider."""
        from app.backend.agent import create_model_from_config

        config = LLMConfig(
            provider="unsupported",  # type: ignore
            model="test",
            temperature=0.7,
            timeout=30,
        )

        with pytest.raises(ValueError, match="Unsupported provider"):
            create_model_from_config(config)


class TestRestaurantSearchAgent:
    """Tests for RestaurantSearchAgent."""

    @pytest.mark.asyncio
    @patch("app.backend.agent.Agent")
    @patch("app.backend.agent.create_model_from_config")
    async def test_search_async_returns_info(self, mock_create_model, mock_agent_class):
        """Test successful async search returns RestaurantInfo."""
        from app.backend.agent import RestaurantInfo, RestaurantSearchAgent

        # Setup mocks
        mock_result = Mock()
        mock_result.output = RestaurantInfo(
            address="123 Main St",
            phone="555-1234",
            hours="9am-10pm",
            website="https://example.com",
            description="A test restaurant",
        )
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent
        mock_create_model.return_value = Mock()

        config = LLMConfig(
            provider="ollama",
            model="test",
            temperature=0.7,
            timeout=30,
            ollama_host="http://localhost:11434",
        )

        agent = RestaurantSearchAgent(zip_code="73107", llm_config=config)
        result = await agent.search_async("Test Restaurant")

        assert result is not None
        assert result.address == "123 Main St"
        assert result.phone == "555-1234"
        assert result.hours == "9am-10pm"

    @pytest.mark.asyncio
    @patch("app.backend.agent.Agent")
    @patch("app.backend.agent.create_model_from_config")
    async def test_search_async_handles_error(self, mock_create_model, mock_agent_class):
        """Test async search handles errors gracefully."""
        from app.backend.agent import RestaurantSearchAgent

        # Setup mock to raise exception
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=Exception("API Error"))
        mock_agent_class.return_value = mock_agent
        mock_create_model.return_value = Mock()

        config = LLMConfig(
            provider="ollama",
            model="test",
            temperature=0.7,
            timeout=30,
            ollama_host="http://localhost:11434",
        )

        agent = RestaurantSearchAgent(zip_code="73107", llm_config=config)
        result = await agent.search_async("Test Restaurant")

        assert result is None

    @patch("app.backend.agent.Agent")
    @patch("app.backend.agent.create_model_from_config")
    def test_search_sync_returns_info(self, mock_create_model, mock_agent_class):
        """Test sync search wrapper works correctly."""
        from app.backend.agent import RestaurantInfo, RestaurantSearchAgent

        # Setup mocks - need async mock for the run method
        mock_result = Mock()
        mock_result.output = RestaurantInfo(
            address="456 Oak Ave",
            phone="555-5678",
        )
        mock_agent = Mock()
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent
        mock_create_model.return_value = Mock()

        config = LLMConfig(
            provider="ollama",
            model="test",
            temperature=0.7,
            timeout=30,
            ollama_host="http://localhost:11434",
        )

        agent = RestaurantSearchAgent(zip_code="73107", llm_config=config)
        result = agent.search("Test Restaurant")

        assert result is not None
        assert result.address == "456 Oak Ave"


class TestLookupRestaurantInfo:
    """Tests for convenience lookup functions."""

    @patch("requests.post")
    @patch("app.backend.agent.get_llm_config")
    @patch("app.backend.agent.get_app_config")
    def test_lookup_restaurant_info_uses_default_config(self, mock_get_app_config, mock_get_llm_config, mock_post):
        """Test lookup_restaurant_info uses default app config and calls Ollama API."""
        from app.backend.agent import RestaurantInfo, lookup_restaurant_info
        from app.config import LLMConfig

        mock_get_app_config.return_value = {"zip_code": "73107"}
        mock_get_llm_config.return_value = LLMConfig(
            provider="ollama",
            model="qwen3:8b",
            temperature=0.7,
            timeout=30,
            ollama_host="http://localhost:11434",
        )

        mock_response = Mock()
        mock_response.json.return_value = {
            "response": '{"address": "123 Test St", "phone": "555-1234", "hours": null, "website": null, "description": "A test restaurant"}'
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = lookup_restaurant_info("Test Restaurant")

        mock_get_app_config.assert_called_once()
        mock_get_llm_config.assert_called_once()
        mock_post.assert_called_once()
        # Verify Ollama API was called
        call_args = mock_post.call_args
        assert (
            "http://localhost:11434/api/generate" in call_args[0]
            or call_args[1].get("url", call_args[0][0]) == "http://localhost:11434/api/generate"
        )
        assert result is not None
        assert result.address == "123 Test St"
        assert result.phone == "555-1234"
