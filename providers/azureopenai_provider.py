import json
import sys
import traceback

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
            response = self.client.responses.create(
                model="gpt-5.4-mini",
                input=messages,
                tools=self.tools,
                store=False,
                tool_choice="auto" if tools else "none",
                stream=False,
            )

            parsed_tool_calls = []
            text_content = None

            # response.output es una lista de items tipados
            for item in response.output:
                if item.type == "function_call":
                    tool_call = ToolCall(
                        id=item.call_id,
                        function_name=item.name,
                        arguments=json.loads(item.arguments),
                    )
                    parsed_tool_calls.append(tool_call)

                elif item.type == "message":
                    # Saco el texto del assistant
                    for content_part in item.content:
                        if content_part.type == "output_text":
                            text_content = content_part.text

            return ProviderResponse(
                content=text_content,
                tool_calls=parsed_tool_calls,
                # Guardamos los items crudos de function_call para el historial
                raw_tool_calls_data=[
                    item for item in response.output if item.type == "function_call"
                ],
            )

        except OpenAIError as e:
            raise AIProviderError(f"Error en evaluación síncrona (Azure OpenAI): {e}") from e

        except Exception as e:
            print(f"\n[!!!] ERROR ATRAPADO: {e}\n", file=sys.stdout)
            # 2. Obliga a imprimir el traceback por la misma salida normal
            traceback.print_exc(file=sys.stdout)
            raise

    def generate_streaming_response(self, messages: list, max_output_tokens: int = 3000):

        try:
            stream = self.client.responses.create(
                model="gpt-5.4-mini",
                input=messages,
                tools=self.tools,
                store=False,
                max_output_tokens=max_output_tokens,
                stream=True,
            )

            for event in stream:
                # Texto delta
                if event.type == "response.output_text.delta":
                    yield event.delta

                # Métricas finales
                elif event.type == "response.completed":
                    usage = event.response.usage
                    if usage:
                        yield UsageMetadata(
                            input_tokens=usage.input_tokens,
                            output_tokens=usage.output_tokens,
                            total_tokens=usage.total_tokens,
                        )

        except OpenAIError as e:
            # raise AIProviderError(f"Azure OpenAI API error: {e}") from e
            print("\n===== OPENAI ERROR DEBUG =====")
            print(e)
            print(getattr(e, "response", None))
            print(getattr(e, "body", None))
            print("================================\n")
            raise
