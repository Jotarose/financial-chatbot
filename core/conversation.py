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
