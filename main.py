from core import ConversationManager, FallbackChatbot, settings
from core.prompts import FINANCIAL_SYSTEM_PROMPT
from providers import AzureOpenAIProvider, GeminiProvider, OllamaProvider
from utils.management_utils import show_commands
from utils.provider_utils import select_provider


def main():

    # Configure all the setup
    providers = {
        "gemini": GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            name="Gemini",
        ),
        "azureopenai": AzureOpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            endpoint=settings.OPENAI_BASE_URL,
            name="Azure OpenAI",
        ),
        "ollama": OllamaProvider(
            api_key=settings.OLLAMA_API_KEY,
            endpoint=settings.OLLAMA_BASE_URL,
            name="Ollama (Local)",
        ),
    }
    main_provider, fallback_provider = select_provider(providers)

    conversation_manager = ConversationManager(
        system_prompt=FINANCIAL_SYSTEM_PROMPT, max_messages=10
    )

    chatbot = FallbackChatbot(
        main_provider=main_provider,
        fallback_provider=fallback_provider,
        conversation_manager=conversation_manager,
    )

    print("Hello from financial-agent!\n")
    chatbot.show_commands()

    try:
        while True:
            user_input = input("\nYou: ").strip()

            # (/estadisticas, /limpiar, /cambiar, /ayuda, /salir).
            match user_input:
                case "/salir":
                    chatbot.show_statistics()
                    print("\nSaliendo del chatbot financiero ...")
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
                    chatbot.show_statistics()
                    continue

                case _:
                    pass

            print("Assistant:", end=" ", flush=True)

            try:
                for chunk in chatbot.generate_streaming_response(user_input):
                    print(chunk, end="", flush=True)
                print()  # Newline after the assistant's response

            except Exception as e:
                print(f"\n[Error de conexión con el proveedor]: {e}")
                print("Por favor, intenta hacer tu pregunta de nuevo.")

    except KeyboardInterrupt:
        # Si el usuario hace Ctrl+C, salimos elegantemente
        print("\n\nCierre forzado detectado. ¡Hasta pronto!")


if __name__ == "__main__":
    main()
