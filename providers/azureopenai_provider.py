from openai import OpenAI, OpenAIError

from .generic_provider import AIProvider, AIProviderError


class AzureOpenAIProvider(AIProvider):
    def __init__(self, api_key: str, endpoint: str, name: str):
        super().__init__(api_key, name)
        self.client = OpenAI(api_key=api_key, base_url=endpoint)

    def generate_streaming_response(self, messages: list, max_output_tokens: int = 1024):
        try:
            response_stream = self.client.responses.create(
                model="gpt-5.4-mini",
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

        except OpenAIError as e:
            raise AIProviderError(f"Azure OpenAI API error: {e}") from e
