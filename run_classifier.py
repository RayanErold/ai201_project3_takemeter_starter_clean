"""CLI fallback for the TakeMeter classifier."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root so the key works without setting a shell variable.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from app import classify, DEFAULT_MODEL  # noqa: E402


def main() -> None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set in the environment or .env file. "
            "Create a .env file with GROQ_API_KEY=... or export it before running."
        )

    text = input("Enter a Reddit post or comment:\n").strip()
    if not text:
        print("No text entered. Exiting.")
        return

    label, confidence, raw = classify(text, DEFAULT_MODEL)
    if label is None:
        print("Could not parse a valid label from the model response.")
        print("Raw model output:\n", raw)
        return

    print(f"Predicted label: {label}")
    if confidence is not None:
        print(f"Confidence: {confidence:.0%}")
    print("\nRaw model output:\n", raw)


if __name__ == "__main__":
    main()
