from core import settings

from .azureopenai_provider import AzureOpenAIProvider
from .gemini_provider import GeminiProvider
from .ollama_provider import OllamaProvider


def create_providers():
    # Configure all the providers setup
    return {
        "gemini": GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            name="Gemini",
        ),
        "azureopenai": AzureOpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            endpoint=settings.OPENAI_BASE_URL,
            name="Azure OpenAI",
        ),
        "ollama": OllamaProvider(
            api_key=settings.OLLAMA_API_KEY,
            endpoint=settings.OLLAMA_BASE_URL,
            name="Ollama (Local)",
        ),
    }
