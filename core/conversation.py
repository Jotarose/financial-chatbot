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

    def add_assistant_tool_call(self, message_content: str | None, raw_tool_calls: list):
        """
            Registra la petición del modelo para usar una o varias herramientas.
            Requiere el objeto crudo de la API para mantener el formato interno.
            En la Responses API los function_call son items independientes en el output.
        Los guardamos tal cual para reenviarlos en el siguiente turno.
        """

        # Primero el mensaje de texto del assistant si lo hay
        if message_content:
            self.history.append({"role": "assistant", "content": message_content})

        # Luego cada function call como item separado
        for fc_item in raw_tool_calls:
            self.history.append(
                {
                    "type": "function_call",
                    "id": fc_item.id,
                    "call_id": fc_item.call_id,
                    "name": fc_item.name,
                    "arguments": fc_item.arguments,
                }
            )

    def add_tool_result(self, tool_call_id: str, result: str):
        """
            En la Responses API el resultado va como item de tipo function_call_output.
        El campo clave es "call_id" (no "tool_call_id").
        """
        self.history.append(
            {
                "type": "function_call_output",
                "call_id": tool_call_id,  # ← cambio crítico
                "output": result,  # ← "output" en vez de "content"
            }
        )
