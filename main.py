import os

from dotenv import load_dotenv

from core import ConversationManager, FallbackChatbot
from providers import AzureOpenAIProvider, GeminiProvider, OllamaProvider
from utils.management_utils import show_commands
from utils.provider_utils import select_provider

load_dotenv()


def main():

    # Configure all the setup
    providers = {
        "gemini": GeminiProvider(
            api_key=os.getenv("GEMINI_API_KEY"),
            name="Gemini",
        ),
        "azureopenai": AzureOpenAIProvider(
            api_key=os.getenv("OPENAI_API_KEY"),
            endpoint=os.getenv("OPENAI_BASE_URL"),
            name="Azure OpenAI",
        ),
        "ollama": OllamaProvider(
            api_key=os.getenv("OLLAMA_API_KEY"),
            endpoint=os.getenv("OLLAMA_BASE_URL"),
            name="Ollama (Local)",
        ),
    }
    main_provider, fallback_provider = select_provider(providers)

    system_prompt = "You are a helpful financial assistant. Answer questions about finance and provide insights based on the latest market trends. Be professional and concise in your responses. Do not invent information, and if you don't know the answer, say so. All the answers must be in the same language as the user's question (Default: In Spanish)."

    conversation_manager = ConversationManager(system_prompt=system_prompt, max_messages=10)

    chatbot = FallbackChatbot(
        main_provider=main_provider,
        fallback_provider=fallback_provider,
        conversation_manager=conversation_manager,
    )

    print("Hello from financial-agent!\n")
    show_commands()

    while True:
        user_input = input("\nYou: ").strip()

        # (/estadisticas, /limpiar, /cambiar, /ayuda, /salir).
        match user_input:
            case "/salir":
                print("Saliendo del chatbot financiero ...")
                break

            case "/limpiar":
                chatbot.clean_history()
                print("Assistant: He limpiado la memoria del chatbot\n")
                continue

            case "/cambiar":
                main_provider, fallback_provider = select_provider(providers)
                chatbot.change_provider(main_provider, fallback_provider)
                names = chatbot.get_providers_names()
                print(
                    f"Assistant: Proveedor principal cambiado a {names[0]} y el proveedor de fallback a cambiado a {names[1]}\n"
                )
                continue

            case "/ayuda":
                show_commands()
                continue

            case "/estadisticas":
                statistics = chatbot.get_statistics()
                print("\nESTADISTICAS DE LA SESION:")
                for key, value in statistics.items():
                    print(f"- {key.capitalize()}: {value}")
                continue

            case _:
                pass

        print("Assistant:", end=" ", flush=True)
        for chunk in chatbot.generate_streaming_response(user_input):
            print(chunk, end="", flush=True)
        print()  # Newline after the assistant's response


if __name__ == "__main__":
    main()
