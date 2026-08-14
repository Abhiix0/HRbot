from hrbot.config import load_env
from hrbot.core.service import stream_response
from hrbot.providers.base import ProviderError


def main() -> None:
    load_env()
    print("HRBot ready. Type 'quit' to exit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession closed.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break

        print("Bot: ", end="", flush=True)
        try:
            for chunk in stream_response(user_input):
                print(chunk, end="", flush=True)
            print("\n")
        except ProviderError as exc:
            print(f"\n[Sorry, I couldn't get a response: {exc}]\n")


if __name__ == "__main__":
    main()
