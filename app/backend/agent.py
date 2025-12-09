"""
AI Agent module for restaurant information lookup.

Uses pydantic-ai with duckduckgo_search_tool to find restaurant details.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for direct execution
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.backend.logging import start_action
from app.config import LLMConfig, get_app_config, get_llm_config
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent

# Custom synchronous duckduckgo search tool to avoid ThreadPoolExecutor issues
try:
    from ddgs.ddgs import DDGS
except ImportError as _import_error:
    raise ImportError(
        'Please install `ddgs` to use the DuckDuckGo search tool, '
        'you can use the `duckduckgo` optional group — `pip install "pydantic-ai-slim[duckduckgo]"`'
    ) from _import_error
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.tools import Tool
from typing import Any


def sync_duckduckgo_search_tool(max_results: int | None = None):
    """Creates a synchronous DuckDuckGo search tool that avoids ThreadPoolExecutor issues."""

    def search_duckduckgo(query: str) -> list[dict[str, str]]:
        """Synchronous DuckDuckGo search using direct HTTP requests."""
        import requests
        import urllib.parse

        try:
            # Use DuckDuckGo's instant answers API which is synchronous
            search_url = "https://api.duckduckgo.com/"
            params = {'q': f"{query} restaurant near {73107}", 'format': 'json', 'no_html': '1', 'skip_disambig': '1'}

            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []

            # Add the instant answer if available
            if data.get('AbstractText'):
                results.append(
                    {
                        "title": data.get('Heading', query),
                        "href": data.get('AbstractURL', ''),
                        "body": data.get('AbstractText', ''),
                    }
                )

            # Add related topics
            for topic in data.get('RelatedTopics', [])[:3]:  # Limit to 3 results
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append(
                        {
                            "title": topic.get('FirstURL', '').split('/')[-1]
                            if topic.get('FirstURL')
                            else topic.get('Text', '')[:50],
                            "href": topic.get('FirstURL', ''),
                            "body": topic.get('Text', ''),
                        }
                    )

            # If no results, return a basic fallback
            if not results:
                results = [
                    {
                        "title": f"Search results for {query}",
                        "href": f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                        "body": f"Restaurant information for {query} - search results may be limited.",
                    }
                ]

            return results[: max_results or 5]

        except Exception as e:
            # Fallback if anything fails
            return [
                {
                    "title": f"Search results for {query}",
                    "href": f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                    "body": f"Unable to search for {query} at this time: {str(e)}",
                }
            ]

    return Tool[Any](
        search_duckduckgo,
        name='duckduckgo_search',
        description='Searches DuckDuckGo for the given query and returns the results.',
    )


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
        ValueError: If provider is not supported or required credentials missing
    """
    if config.provider == "ollama":
        if not config.ollama_host:
            raise ValueError("OLLAMA_HOST is required for ollama provider")
        return OpenAIChatModel(
            model_name=config.model,
            provider=OllamaProvider(base_url=f"{config.ollama_host}/v1"),
        )
    elif config.provider == "openrouter":
        if not config.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is required for openrouter provider")
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
            tools=[sync_duckduckgo_search_tool()],
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
        Sync wrapper for search_async using a separate thread with isolated httpx client.

        In Flet desktop mode, the global ThreadPoolExecutor gets shut down.
        We run the async search in a separate thread with httpx configured to avoid threading.

        Args:
            restaurant_name: Name of the restaurant to search for

        Returns:
            RestaurantInfo with found details, or None on error
        """
        import concurrent.futures
        import httpx
        import threading

        # Create a new event loop in a separate thread to avoid
        # ThreadPoolExecutor conflicts with Flet's desktop mode
        def run_in_thread():
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Save original AsyncClient before monkey patching
            original_async_client = httpx.AsyncClient

            # Configure httpx to use synchronous client to avoid ThreadPoolExecutor
            httpx.AsyncClient = httpx.Client  # Monkey patch to use sync client

            try:
                return loop.run_until_complete(self.search_async(restaurant_name))
            finally:
                # Restore original AsyncClient to avoid polluting global state
                httpx.AsyncClient = original_async_client
                loop.close()

        # Run the async search in a separate thread with its own event loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_in_thread)
            try:
                return future.result(timeout=30)  # 30 second timeout
            except concurrent.futures.TimeoutError:
                return None


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

    For Flet desktop mode, we use a simplified synchronous approach
    to avoid ThreadPoolExecutor conflicts.

    Args:
        restaurant_name: Name of the restaurant

    Returns:
        RestaurantInfo or None on error
    """
    import json
    import requests
    from eliot import log_message

    log_message(message_type="lookup_info_start", restaurant=restaurant_name)
    app_config = get_app_config()

    try:
        # Use a simple synchronous approach that doesn't rely on pydantic-ai
        # This avoids the httpx ThreadPoolExecutor issues in Flet desktop mode

        # Get LLM config
        llm_config = get_llm_config()

        if llm_config.provider == "ollama":
            # Use Ollama API directly with synchronous requests
            ollama_url = f"{llm_config.ollama_host}/api/generate"

            prompt = f"""Find information about the restaurant "{restaurant_name}" near zip code {app_config["zip_code"]}.

Search for and return ONLY factual information in this exact JSON format:
{{
    "address": "street address or null",
    "phone": "phone number or null",
    "hours": "operating hours or null",
    "website": "website URL or null",
    "description": "brief description or null"
}}

If you cannot find specific information, use null for that field. Do not make up information."""

            payload = {"model": llm_config.model, "prompt": prompt, "stream": False, "format": "json"}

            response = requests.post(ollama_url, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "{}")

            # Parse the JSON response
            try:
                data = json.loads(response_text.strip())
                return RestaurantInfo(
                    address=data.get("address"),
                    phone=data.get("phone"),
                    hours=data.get("hours"),
                    website=data.get("website"),
                    description=data.get("description"),
                )
            except json.JSONDecodeError:
                log_message(message_type="lookup_info_parse_error", error="Invalid JSON response")
                return None

        elif llm_config.provider == "openrouter":
            # Use OpenRouter API directly with synchronous requests
            openrouter_url = "https://openrouter.ai/api/v1/chat/completions"

            prompt = f"""Find information about the restaurant "{restaurant_name}" near zip code {app_config["zip_code"]}.

Search for and return ONLY factual information in this exact JSON format:
{{
    "address": "street address or null",
    "phone": "phone number or null",
    "hours": "operating hours or null",
    "website": "website URL or null",
    "description": "brief description or null"
}}

If you cannot find specific information, use null for that field. Do not make up information."""

            headers = {"Authorization": f"Bearer {llm_config.openrouter_api_key}", "Content-Type": "application/json"}

            payload = {
                "model": llm_config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": llm_config.temperature,
                "max_tokens": 500,
            }

            response = requests.post(openrouter_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")

            # Parse the JSON response
            try:
                data = json.loads(response_text.strip())
                return RestaurantInfo(
                    address=data.get("address"),
                    phone=data.get("phone"),
                    hours=data.get("hours"),
                    website=data.get("website"),
                    description=data.get("description"),
                )
            except json.JSONDecodeError:
                log_message(message_type="lookup_info_parse_error", error="Invalid JSON response")
                return None

        else:
            # For other providers, fall back to the pydantic-ai approach
            # This may still have issues in Flet desktop mode
            log_message(message_type="lookup_info_fallback_provider", provider=llm_config.provider)
            agent = RestaurantSearchAgent(zip_code=app_config["zip_code"])
            log_message(message_type="lookup_info_agent_created")
            result = agent.search(restaurant_name)
            return result

    except Exception as e:
        log_message(message_type="lookup_info_error", error=str(e))
        return None
    finally:
        log_message(message_type="lookup_info_complete", found=False)  # Will be overridden if successful
