import json

from openai import OpenAI, OpenAIError

from schemas.provider_response import ProviderResponse, ToolCall
from schemas.usage_metadata import UsageMetadata
from tools.registry import tools

from .generic_provider import AIProvider, AIProviderError


class AzureOpenAIProvider(AIProvider):
    def __init__(self, api_key: str, endpoint: str, name: str):
        super().__init__(api_key, name)
        self.client = OpenAI(api_key=api_key, base_url=endpoint)
        self.tools = tools

    def evaluate_tools(self, messages: list) -> ProviderResponse:
        try:
            response = self.client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto" if tools else "none",
                stream=False,
            )

            message = response.choices[0].message
            parsed_tool_calls = []

            # Procesamiento adaptado a la estructura de chat.completions
            if message.tool_calls:
                for tool in message.tool_calls:
                    parsed_tool_calls.append(
                        ToolCall(
                            id=tool.id,
                            nombre=tool.function.name,
                            argumentos=json.loads(tool.function.arguments),
                        )
                    )

            return ProviderResponse(
                content=message.content,
                tool_calls=parsed_tool_calls,
                raw_tool_calls_data=message.tool_calls,  # Se almacena la lista de tool_calls nativa
            )

        except OpenAIError as e:
            raise AIProviderError(f"Error en evaluación síncrona (Azure OpenAI): {e}") from e

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
                if event.type == "response.completed":
                    final_usage = UsageMetadata(
                        input_tokens=event.response.usage.input_tokens,
                        output_tokens=event.response.usage.output_tokens,
                        total_tokens=event.response.usage.total_tokens,
                    )
                    yield final_usage

        except OpenAIError as e:
            raise AIProviderError(f"Azure OpenAI API error: {e}") from e
