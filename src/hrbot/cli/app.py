from hrbot.config import load_env
from hrbot.core.service import get_response


def main() -> None:
    load_env()
    print("HRBot ready. Type 'quit' to exit.\n")
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
