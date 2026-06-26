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

    def _to_responses(self, messages: list) -> list:
        clean = []

        for m in messages:
            role = m.get("role")
            content = m.get("content")

            # 1. eliminar mensajes inválidos
            if content is None:
                continue

            # 2. eliminar tool calls (clave)
            if m.get("tool_calls"):
                continue

            # 3. eliminar tool messages (opcional pero recomendado aquí)
            if role == "tool":
                continue

            # 4. solo roles válidos
            if role not in ["user", "assistant", "system", "developer"]:
                continue

            clean.append({"role": role, "content": content})

        return clean

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
                    tool_call = ToolCall(
                        id=tool.id,
                        function_name=tool.function.name,
                        arguments=json.loads(tool.function.arguments),
                    )

                    parsed_tool_calls.append(tool_call)

            return ProviderResponse(
                content=message.content,
                tool_calls=parsed_tool_calls,
                raw_tool_calls_data=message.tool_calls,  # Se almacena la lista de tool_calls nativa
            )

        except OpenAIError as e:
            raise AIProviderError(f"Error en evaluación síncrona (Azure OpenAI): {e}") from e
            # 1. Imprime un texto llamativo en la salida normal para saber que entró al except

        except Exception as e:
            print(f"\n[!!!] ERROR ATRAPADO: {e}\n", file=sys.stdout)
            # 2. Obliga a imprimir el traceback por la misma salida normal
            traceback.print_exc(file=sys.stdout)
            raise

    def generate_streaming_response(self, messages: list, max_output_tokens: int = 3000):

        try:
            response_stream = self.client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto" if tools else "none",
                temperature=0.7,
                top_p=0.9,
                max_completion_tokens=max_output_tokens,
                stream=True,
                stream_options={"include_usage": True},
            )

            final_usage = None

            for chunk in response_stream:
                # 1. Validación estricta de la matriz de inferencia
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield delta.content

                # 2. Extracción aislada de métricas (el chunk final no tiene 'choices')
                if hasattr(chunk, "usage") and chunk.usage is not None:
                    final_usage = UsageMetadata(
                        input_tokens=chunk.usage.prompt_tokens,
                        output_tokens=chunk.usage.completion_tokens,
                        total_tokens=chunk.usage.total_tokens,
                    )
                    yield final_usage

        except OpenAIError as e:
            # raise AIProviderError(f"Azure OpenAI API error: {e}") from e
            print("\n===== OPENAI ERROR DEBUG =====")
            print(e)
            print(getattr(e, "response", None))
            print(getattr(e, "body", None))
            print("================================\n")
            raise
