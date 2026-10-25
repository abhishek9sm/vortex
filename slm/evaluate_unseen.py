import csv
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parent
TEST_PATH = BASE_DIR / "unseen_notifications.csv"

MODELS = {
    "Base model": BASE_DIR / "notification_model.joblib",
    "Personalized model": BASE_DIR / "personalized_model.joblib",
}


def main():
    texts = []
    actual_labels = []

    with open(TEST_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            text = row["text"].strip()
            category = row["category"].strip()

            if text and category:
                texts.append(text)
                actual_labels.append(category)

    if not texts:
        raise ValueError("No test examples found.")

    results = {}

    for name, model_path in MODELS.items():
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        model = joblib.load(model_path)
        predictions = model.predict(texts)

        correct = sum(
            actual == predicted
            for actual, predicted in zip(actual_labels, predictions)
        )

        accuracy = accuracy_score(actual_labels, predictions)
        results[name] = (correct, accuracy)

        print(f"\n{'=' * 45}")
        print(name)
        print("=" * 45)
        print(f"Test examples: {len(texts)}")
        print(f"Correct: {correct}/{len(texts)}")
        print(f"Accuracy: {accuracy:.2%}")

        print("\nClassification report:")
        print(
            classification_report(
                actual_labels,
                predictions,
                labels=sorted(set(actual_labels)),
                zero_division=0,
            )
        )

    print("\n========== FINAL COMPARISON ==========")

    for name, (correct, accuracy) in results.items():
        print(f"{name}: {correct}/{len(texts)} ({accuracy:.2%})")

    difference = (
        results["Personalized model"][1]
        - results["Base model"][1]
    ) * 100

    print(f"Accuracy change: {difference:+.2f} percentage points")
    print(
        "\nNote: This test contains only 25 examples. "
        "Results are preliminary, not proof of general performance."
    )


if __name__ == "__main__":
    main()