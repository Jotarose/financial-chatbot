from google import genai
from google.genai import types
from google.genai.errors import APIError

from schemas.usage_metadata import UsageMetadata

from .generic_provider import AIProvider, AIProviderError


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, name: str):
        super().__init__(api_key, name)
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
                if chunk.candidates[0].finish_reason:
                    meta = chunk.usage_metadata
                    thoughts = meta.thoughts_token_count if meta.thoughts_token_count else 0
                    # Mapear a tu esquema UsageMetadata
                    final_usage = UsageMetadata(
                        input_tokens=meta.prompt_token_count,
                        output_tokens=meta.candidates_token_count + thoughts,
                        total_tokens=meta.total_token_count,
                    )

                    # Enviar el objeto de estadísticas al chatbot
                    yield final_usage

                yield chunk.text

        except APIError as e:
            raise AIProviderError(f"Gemini API error: {e}") from e
