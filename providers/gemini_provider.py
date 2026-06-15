from google import genai
from google.genai import types
from google.genai.errors import APIError

from .generic_provider import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = genai.Client(api_key=api_key)

    # set_system_prompt is not needed to be overridden since it just calls the parent method.

    def generate_streaming_response(self, messages: list, max_output_tokens: int = 1024):

        # Adapt the message format to Gemini's expected input
        gemini_history = []
        system_instruction = None

        for message in messages:
            if message["role"] == "assistant":
                gemini_history.append({"role": "model", "parts": [{"text": message["content"]}]})
            elif message["role"] == "developer":
                system_instruction = message["content"]

            else:
                gemini_history.append({"role": "user", "parts": [{"text": message["content"]}]})

        try:
            response_stream = self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=gemini_history,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=max_output_tokens,
                ),
            )

            for chunk in response_stream:
                yield chunk.text

        except APIError as e:
            raise AIProviderError(f"Gemini API error: {e}") from e
