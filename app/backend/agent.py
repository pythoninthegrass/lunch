"""
AI Agent module for restaurant information lookup.

Uses pydantic-ai with duckduckgo_search_tool to find restaurant details.
"""

import asyncio
import nest_asyncio

nest_asyncio.apply()

from app.backend.logging import start_action
from app.config import LLMConfig, get_app_config, get_llm_config
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider


class RestaurantInfo(BaseModel):
    """Structured restaurant information from search."""

    address: str | None = None
    phone: str | None = None
    hours: str | None = None
    website: str | None = None
    description: str | None = None


def create_model_from_config(config: LLMConfig):
    """
    Create a pydantic-ai compatible model from LLMConfig.

    Args:
        config: LLMConfig instance with provider settings

    Returns:
        Configured pydantic-ai model

    Raises:
        ValueError: If provider is not supported
    """
    if config.provider == "ollama":
        return OpenAIChatModel(
            model_name=config.model,
            provider=OllamaProvider(base_url=f"{config.ollama_host}/v1"),
        )
    elif config.provider == "openrouter":
        return OpenAIChatModel(
            config.model,
            provider=OpenRouterProvider(api_key=config.openrouter_api_key),
        )
    raise ValueError(f"Unsupported provider: {config.provider}")


@dataclass
class RestaurantSearchAgent:
    """Agent for searching restaurant information."""

    zip_code: str
    llm_config: LLMConfig | None = None

    def __post_init__(self):
        if self.llm_config is None:
            self.llm_config = get_llm_config()
        model = create_model_from_config(self.llm_config)
        system_prompt = f"""You are a restaurant information assistant.
Search for restaurant details near zip code {self.zip_code}.
Find: address, phone, hours, website, brief description.
Return only factual info from search results."""
        self.agent = Agent(
            model,
            tools=[duckduckgo_search_tool()],
            output_type=RestaurantInfo,
            system_prompt=system_prompt,
            retries=5,
        )

    async def search_async(self, restaurant_name: str) -> RestaurantInfo | None:
        """
        Async search for restaurant info.

        Args:
            restaurant_name: Name of the restaurant to search for

        Returns:
            RestaurantInfo with found details, or None on error
        """
        with start_action(action_type="agent_search", restaurant=restaurant_name) as action:
            try:
                result = await self.agent.run(f"Find information about: {restaurant_name}")
                action.add_success_fields(found=result.output is not None)
                return result.output
            except Exception as e:
                action.add_success_fields(error=str(e))
                return None

    def search(self, restaurant_name: str) -> RestaurantInfo | None:
        """
        Sync wrapper for search_async using nest_asyncio.

        nest_asyncio allows running asyncio.run() even when an event loop
        is already running (like in Flet's context).

        Args:
            restaurant_name: Name of the restaurant to search for

        Returns:
            RestaurantInfo with found details, or None on error
        """
        return asyncio.run(self.search_async(restaurant_name))


async def lookup_restaurant_info_async(restaurant_name: str) -> RestaurantInfo | None:
    """
    Async convenience function with default config.

    Args:
        restaurant_name: Name of the restaurant

    Returns:
        RestaurantInfo or None on error
    """
    app_config = get_app_config()
    agent = RestaurantSearchAgent(zip_code=app_config["zip_code"])
    return await agent.search_async(restaurant_name)


def lookup_restaurant_info(restaurant_name: str) -> RestaurantInfo | None:
    """
    Sync convenience function with default config.

    Args:
        restaurant_name: Name of the restaurant

    Returns:
        RestaurantInfo or None on error
    """
    from eliot import log_message

    log_message(message_type="lookup_info_start", restaurant=restaurant_name)
    app_config = get_app_config()
    log_message(message_type="lookup_info_config", zip_code=app_config["zip_code"])
    agent = RestaurantSearchAgent(zip_code=app_config["zip_code"])
    log_message(message_type="lookup_info_agent_created")
    result = agent.search(restaurant_name)
    log_message(message_type="lookup_info_complete", found=result is not None)
    return result
