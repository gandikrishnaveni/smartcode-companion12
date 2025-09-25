from functools import lru_cache
from smart_code_companion.core.config import get_settings
# Use relative imports to correctly reference modules within the same package
from .base import AIClient
from .mock import MockAIClient
from .google import GoogleGeminiClient
from .ibm import IBMWatsonClient


@lru_cache()
def get_ai_client() -> AIClient:
    """
    Factory function to get the configured AI client.
    This function is the central point for creating AI client instances.
    """
    settings = get_settings()
    provider = settings.AI_PROVIDER

    if provider == "mock":
        return MockAIClient()
    if provider == "google":
        return GoogleGeminiClient(settings=settings)
    if provider == "ibm":
        return IBMWatsonClient()

    raise ValueError(f"Unknown AI provider configured: {provider}")
