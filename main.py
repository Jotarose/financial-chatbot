import os

from dotenv import load_dotenv

from core import ConversationManager, FallbackChatbot
from providers import AzureOpenAIProvider, GeminiProvider, OllamaProvider, select_provider

load_dotenv()


def main():
    print("Hello from financial-agent!\n")

    # Configure all the setup
    providers = {
        "gemini": GeminiProvider(api_key=os.getenv("GEMINI_API_KEY")),
        "azureopenai": AzureOpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY"),
            endpoint=os.getenv("OPENAI_BASE_URL"),
        ),
        "ollama": OllamaProvider(
            api_key=os.getenv("OLLAMA_API_KEY"),
            endpoint=os.getenv("OLLAMA_BASE_URL"),
        ),
    }
    main_provider, fallback_provider = select_provider(providers)

    system_prompt = "You are a helpful financial assistant. Answer questions about finance and provide insights based on the latest market trends. Be professional and concise in your responses. Do not invent information, and if you don't know the answer, say so. All the answers must be in the same language as the user's question."

    conversation_manager = ConversationManager(system_prompt=system_prompt, max_messages=10)

    chatbot = FallbackChatbot(
        primary_provider=main_provider,
        fallback_provider=fallback_provider,
        conversation_manager=conversation_manager,
    )

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"/salir", "/exit"}:
            print("Goodbye!")
            break

        print("Assistant:", end=" ", flush=True)
        for chunk in chatbot.generate_streaming_response(user_input):
            print(chunk, end="", flush=True)
        print()  # Newline after the assistant's response


if __name__ == "__main__":
    main()
