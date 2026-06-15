from openai import OpenAI, OpenAIError

from .generic_provider import AIProvider, AIProviderError


class OllamaProvider(AIProvider):
    def __init__(self, api_key: str, endpoint: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key, base_url=endpoint)

    def generate_streaming_response(self, messages: list, max_output_tokens: int = 1024):
        try:
            response_stream = self.client.responses.create(
                model="gemma3:1b",
                input=messages,
                instructions=self.system_prompt,
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=max_output_tokens,
                stream=True,
            )

            for event in response_stream:
                if event.type == "response.output_text.delta":
                    yield event.delta

        except OpenAIError as e:
            raise AIProviderError(f"Ollama Local API error: {e}") from e
