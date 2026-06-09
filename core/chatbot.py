from core.conversation import ConversationManager
from providers import AIProvider, AIProviderError


class FallbackChatbot:
    """A chatbot that uses a primary LLM provider and falls back to
    a secondary provider if the primary fails."""

    def __init__(
        self,
        primary_provider: AIProvider,
        fallback_provider: AIProvider,
        conversation_manager: ConversationManager,
    ):
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider
        self.conversation = conversation_manager

    def generate_streaming_response(self, user_message: str):
        # Add the user's message to the conversation history
        self.conversation.add_message("user", user_message)
        history = self.conversation.get_api_history()

        full_response = ""

        try:
            # Generate a streaming response from the primary provider
            stream = self.primary_provider.generate_streaming_response(history)
            for chunk in stream:
                if chunk is not None:
                    full_response += chunk
                    yield chunk

        # It can fail in the middle of the stream, so catch the error and fallback to the 2provider
        except AIProviderError as e:
            print(f"Primary provider failed with error: {e}. Falling back to secondary provider.")

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
        return
