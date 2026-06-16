import time

from core.conversation import ConversationManager
from providers import AIProvider, AIProviderError


class FallbackChatbot:
    """A chatbot that uses a primary LLM provider and falls back to
    a secondary provider if the primary fails."""

    def __init__(
        self,
        main_provider: AIProvider,
        fallback_provider: AIProvider,
        conversation_manager: ConversationManager,
    ):
        self.main_provider = main_provider
        self.fallback_provider = fallback_provider
        self.conversation = conversation_manager
        self.statistics = {
            "requests": 0,
            "usage_time": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    def clean_history(self):
        self.conversation.clean_history()

    def get_providers_names(self) -> list:
        return [self.main_provider.get_provider_name(), self.fallback_provider.get_provider_name()]

    def get_statistics(self) -> dict:
        return self.statistics

    def change_provider(self, main_provider: AIProvider, fallback_provider: AIProvider):
        self.main_provider = main_provider
        self.fallback_provider = fallback_provider

    def _add_statistics(self, call_time, p_tokens=None, c_tokens=None):
        """Método interno para acumular métricas después de cada llamada."""
        self.statistics["requests"] += 1
        # self.statistics["prompt_tokens"] += p_tokens
        # self.statistics["completion_tokens"] += c_tokens
        # self.statistics["total_tokens"] += (p_tokens + c_tokens)
        self.statistics["usage_time"] += call_time

    def generate_streaming_response(self, user_message: str):
        start_time = time.perf_counter()

        # Add the user's message to the conversation history
        self.conversation.add_message("user", user_message)
        history = self.conversation.get_api_history()

        full_response = ""

        try:
            # Generate a streaming response from the main provider
            stream = self.main_provider.generate_streaming_response(history)
            for chunk in stream:
                if chunk is not None:
                    full_response += chunk
                    yield chunk

        # It can fail in the middle of the stream, so catch the error and fallback to the 2provider
        except AIProviderError as e:
            print(f"Main provider failed with error: {e}. Falling back to secondary provider.")

            if full_response:
                yield "\n*[Inestable conection, switching to fallback provider...]*\n"

            # Retry generating the response with the fallback provider
            full_response = ""
            try:
                stream = self.fallback_provider.generate_streaming_response(history)
                for chunk in stream:
                    if chunk is not None:
                        full_response += chunk
                        yield chunk

            except AIProviderError as fallback_error:
                # Both providers failed
                print(f"Fallback provider also failed with error: {fallback_error}.")
                err_msg = "\n*[Both providers failed. Please try again later.]*\n"
                yield err_msg
                full_response += err_msg

        # After the full response is received, add it to the conversation history
        if full_response:
            self.conversation.add_message("assistant", full_response)

        stop_time = time.perf_counter()
        call_time = round((stop_time - start_time) * 1000, 2)

        self._add_statistics(call_time)

        return
