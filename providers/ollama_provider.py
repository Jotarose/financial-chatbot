from openai import OpenAI, OpenAIError

from schemas.usage_metadata import UsageMetadata

from .generic_provider import AIProvider, AIProviderError


class OllamaProvider(AIProvider):
    def __init__(self, api_key: str, endpoint: str, name: str):
        super().__init__(api_key, name)
        self.client = OpenAI(api_key=api_key, base_url=endpoint)

    def generate_streaming_response(self, messages: list, max_output_tokens: int = 1024):
        try:
            response_stream = self.client.responses.create(
                model="gemma3:1b",
                input=messages,
                instructions=messages[0]["content"],
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=max_output_tokens,
                stream=True,
            )

            for event in response_stream:
                if event.type == "response.output_text.delta":
                    yield event.delta
                if event.type == "response.completed":
                    final_usage = UsageMetadata(
                        input_tokens=event.response.usage.input_tokens,
                        output_tokens=event.response.usage.output_tokens,
                        total_tokens=event.response.usage.total_tokens,
                    )
                    yield final_usage

        except OpenAIError as e:
            raise AIProviderError(f"Ollama Local API error: {e}") from e
