from abc import ABC, abstractmethod


class AIProviderError(Exception):
    """Custom exception for AI provider errors."""

    pass


class AIProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.system_prompt = None
        self.client = None  # Placeholder for the actual client implementation

    def set_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt

    @abstractmethod
    def generate_streaming_response(self, messages: list, max_output_tokens: int = 1024):
        """
        Generates a streaming response from the specific LLM provider.

        Args:
            messages (list): The conversation history formatted for the API.
        """
        pass
