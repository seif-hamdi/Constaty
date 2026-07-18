from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from constaty_insurance.crew import ConstatyInsuranceCrew


def normalize_image_path(value: str) -> str:
    value = value.strip()
    if not value or value.startswith(("http://", "https://")):
        return value or "No image provided"

    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return str(path)


def run() -> None:
    print("Describe the accident from your point of view.")
    incident_statement = input("> ").strip()
    image_path = normalize_image_path(
        input("Proof image path or URL (press Enter if unavailable): ")
    )

    result = ConstatyInsuranceCrew().crew().kickoff(
        inputs={
            "incident_statement": incident_statement,
            "image_path": image_path,
            "historical_claim_context": "No historical claim context was provided.",
        }
    )

    print("\nFinal report:\n")
    print(result)


if __name__ == "__main__":
    run()
