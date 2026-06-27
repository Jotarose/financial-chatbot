import sys
import time
import traceback
from datetime import datetime

from core.conversation import ConversationManager
from providers import AIProvider, AIProviderError
from schemas.usage_metadata import UsageMetadata
from tools.registry import tool_router


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
            "messages": 0,
            "usage_time": 0.0,
            "start_time": datetime.now(),
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
        }

    def clean_history(self):
        self.conversation.clean_history()

    def show_commands(self):
        print("---- Comandos disponibles ----")
        print(
            "- /salir: Salir del programa.\n"
            "- /limpiar: limpiar el historial de mensajes.\n"
            "- /cambiar: cambiar el provedor de IA.\n"
            "- /estadisticas: mostrar estadisticas de uso.\n"
            "- /ayuda: imprimir los comandos disponibles.\n"
            "*********************************************\n"
        )

    def show_statistics(self):
        print("\nESTADISTICAS DE LA SESION:")
        for key, value in self.statistics.items():
            print(f"- {key.capitalize()}: {value}")

    def get_providers_names(self) -> list:
        return [self.main_provider.get_provider_name(), self.fallback_provider.get_provider_name()]

    def get_statistics(self) -> dict:
        return self.statistics

    def change_provider(self, main_provider: AIProvider, fallback_provider: AIProvider):
        self.main_provider = main_provider
        self.fallback_provider = fallback_provider

    def _add_statistics(self, call_time, final_usage: UsageMetadata | None):
        """Método interno para acumular métricas después de cada llamada."""

        input_tokens = final_usage.input_tokens
        output_tokens = final_usage.output_tokens
        total_tokens = final_usage.total_tokens

        self.statistics["messages"] += 1
        self.statistics["usage_time"] += call_time

        if final_usage:
            self.statistics["total_input_tokens"] += input_tokens
            self.statistics["total_output_tokens"] += output_tokens
            self.statistics["total_tokens"] += total_tokens

    def generate_streaming_response(self, user_message: str):
        start_time = time.perf_counter()

        # Add the user's message to the conversation history
        self.conversation.add_message("user", user_message)

        # FASE 1: Resolucion logica, hay o no hay tools
        max_iterations = 3
        current_iteration = 0

        while current_iteration < max_iterations:
            # history = self.conversation.get_api_history()
            history = self.conversation.get_full_history()
            try:
                # Evaluación síncrona
                provider_response = self.main_provider.evaluate_tools(history)
            except AIProviderError as e:
                print(f"Error evaluando tools: {e}")
                break  # Rompe el bucle lógico ante fallo de red/API, intenta recuperar en Fase 2

            if provider_response.ha_pedido_usar_tools():
                # Registro del estado inmutable
                self.conversation.add_assistant_tool_call(
                    message_content=provider_response.content,
                    raw_tool_calls=provider_response.raw_tool_calls_data,
                )

                # Ejecución enrutada
                for tool_call in provider_response.tool_calls:
                    funcion_ejecutora = tool_router.get(tool_call.function_name)

                    if funcion_ejecutora:
                        try:
                            # Inyección directa de argumentos validados por Pydantic
                            resultado = funcion_ejecutora(**tool_call.arguments)
                            resultado_str = str(resultado)
                            print(f"- Ejecutando: {tool_call.function_name}")
                        except Exception as e:
                            # resultado_str = f"Error interno ejecutando la herramienta: {str(e)}"
                            print(f"Tipo de excepción: {type(e).__name__}")
                            print(f"Mensaje: {e}")
                            traceback.print_exc(file=sys.stdout)
                            raise
                    else:
                        resultado_str = (
                            f"Herramienta '{tool_call.function_name}' no encontrada en el registro."
                        )

                    # Registro del resultado atado al identificador
                    self.conversation.add_tool_result(
                        tool_call_id=tool_call.id,
                        result=resultado_str,
                    )

                current_iteration += 1
                continue
            else:
                # Resolución computacional completada
                self.conversation.add_message(role="assistant", message=provider_response.content)
                break

        # FASE 2: Emision respuesta final al usuario (streaming)
        history = self.conversation.get_api_history()
        full_response = ""
        final_usage = None

        try:
            # Generate a streaming response from the main provider
            stream = self.main_provider.generate_streaming_response(history)
            for chunk in stream:
                if chunk is not None:
                    if isinstance(chunk, str):
                        full_response += chunk
                        yield chunk

                    else:
                        final_usage = chunk

        # It can fail in the middle of the stream
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

        self._add_statistics(call_time, final_usage)

        return
