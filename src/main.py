from src.chatbot.chat import get_response
from src.config.settings import load_env


def main() -> None:
    load_env()
    print("Chatbot ready. Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break
        response = get_response(user_input)
        print(f"Bot: {response}\n")


if __name__ == "__main__":
    main()
