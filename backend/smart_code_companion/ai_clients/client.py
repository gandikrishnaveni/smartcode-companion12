from functools import lru_cache
from smart_code_companion.core.config import get_settings
from .base import AIClient
from .mock import MockAIClient
from .google import GoogleGeminiClient
from .ibm import IBMWatsonClient

@lru_cache()
def get_ai_client() -> AIClient:
    """
    Factory function to get the configured AI client.

    Reads the AI_PROVIDER from the application settings and returns
    an instance of the corresponding client. Uses a cache to ensure
    only one instance of the client is created.

    Raises:
        ValueError: If the configured AI_PROVIDER is not recognized.

    Returns:
        AIClient: An instance of the configured AI client.
    """
    settings = get_settings()
    provider = settings.AI_PROVIDER

    if provider == "mock":
        return MockAIClient()
    if provider == "google":
        # GoogleGeminiClient can still accept settings
        return GoogleGeminiClient(settings=settings)
    if provider == "ibm":
        # Remove settings argument here
        return IBMWatsonClient()

    raise ValueError(f"Unknown AI provider configured: {provider}")
