from core.chatbot import FallbackChatbot
from core.conversation import ConversationManager
from core.prompts import FINANCIAL_SYSTEM_PROMPT
from database import init_db
from providers.factory import create_providers
from utils.provider_utils import select_provider


def main():

    print("Hello from financial-agent!\n")
    # Configure all the setup
    providers = create_providers()
    main_provider, fallback_provider = select_provider(providers)

    print("\n- Configuring the chatbot system ...")
    conversation_manager = ConversationManager(
        system_prompt=FINANCIAL_SYSTEM_PROMPT, max_messages=10
    )

    chatbot = FallbackChatbot(
        main_provider=main_provider,
        fallback_provider=fallback_provider,
        conversation_manager=conversation_manager,
    )
    print(f"- Chatbot fully configured with {main_provider.name} as main provider.\n")

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
                    chatbot.show_commands()
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
    init_db()
    print("System: BBDD started succesfully.")

    main()
