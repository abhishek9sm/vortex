
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "personalized_model.joblib"


def main():
    if not MODEL_PATH.exists():
        print("Personalized model not found. Train it first.")
        raise SystemExit(1)

    model = joblib.load(MODEL_PATH)
    print("Personalized model loaded successfully!")
    print("Enter a notification to classify.")
    print("Type 'exit' to stop.\n")

    while True:
        text = input("Notification: ").strip()

        if text.lower() == "exit":
            break

        if not text:
            print("Please enter a notification.\n")
            continue

        category = model.predict([text])[0]
        probabilities = model.predict_proba([text])[0]
        confidence = max(probabilities)

        print("Predicted category:", category)
        print(f"Model confidence: {confidence:.1%}\n")


if __name__ == "__main__":
    main()
