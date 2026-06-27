from typing import Any


class ConversationManager:
    """Manages LLM conversation history with a sliding window limit.

    Always retains the initial system prompt while limiting recent messages
    to prevent exceeding token limits.

    Args:
        system_prompt (str): Initial system instructions for the LLM.
        max_messages (int, optional): Max recent messages to keep for the API. Defaults to 10."""

    def __init__(self, system_prompt: str, max_messages: int = 10):
        self.system_prompt = system_prompt
        self.history = [
            {
                "role": "developer",
                "content": system_prompt,
            }
        ]
        self.max_messages = max_messages

    def get_api_history(self) -> list:
        """Retrieves truncated history optimized for API context.

        Returns:
            list: The system prompt followed by up to `max_messages` recent messages.
        """
        if len(self.history) > self.max_messages + 1:
            # Calculamos si el historial (sin contar el system_message) supera el límite
            developer_message = self.history[0]
            recent_messages = self.history[1:]

            return [developer_message] + recent_messages[-self.max_messages :]
        else:
            return self.history

    def get_full_history(self) -> list:
        return self.history

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def clean_history(self):
        self.history = [
            {
                "role": "developer",
                "content": self.system_prompt,
            }
        ]

    def add_message(self, role: str, message: str):
        self.history.append({"role": role, "content": message})

    def add_assistant_tool_call(self, message_content: str | None, raw_tool_calls: Any):
        """
        Registra la petición del modelo para usar una o varias herramientas.
        Requiere el objeto crudo de la API para mantener el formato interno.
        """
        self.history.append(
            {
                "role": "assistant",
                "content": message_content,
                "tool_calls": raw_tool_calls,
            }
        )

    def add_tool_result(self, tool_call_id: str, tool_name: str, result: str):
        """
        Registra la salida computacional de la herramienta ejecutada localmente.
        El tool_call_id debe coincidir exactamente con el emitido por el modelo.
        """
        self.history.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            }
        )
