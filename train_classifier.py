
import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


# Project files
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "notifications.csv"
MODEL_PATH = BASE_DIR / "notification_model.joblib"


def load_dataset():
    texts = []
    labels = []

    with open(DATASET_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            text = row["text"].strip()
            category = row["category"].strip()

            if text and category:
                texts.append(text)
                labels.append(category)

    if len(texts) < 10:
        raise ValueError("Please add more training examples.")

    if len(set(labels)) < 2:
        raise ValueError("The dataset needs at least two categories.")

    return texts, labels


def train_model(texts, labels):
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=0.20,
        random_state=42,
        stratify=labels
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                max_features=5000
            )
        ),
        (
            "classifier",
            LogisticRegression(max_iter=1000)
        )
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("\n--- Evaluation ---")
    print(f"Training examples: {len(X_train)}")
    print(f"Test examples: {len(X_test)}")
    print(f"Accuracy: {accuracy_score(y_test, predictions):.2%}")

    print("\nClassification report:")
    print(classification_report(y_test, predictions, zero_division=0))

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH.name}")

    return model


def test_predictions(model):
    examples = [
        "Your examination starts tomorrow",
        "An unusual login was detected on your account",
        "Your package will arrive tomorrow",
        "Flash sale ends tonight",
        "Your friend sent you a message"
    ]

    print("\n--- Sample predictions ---")

    for message in examples:
        category = model.predict([message])[0]

        probabilities = model.predict_proba([message])[0]
        confidence = max(probabilities)

        print(f"\nNotification: {message}")
        print(f"Predicted category: {category}")
        print(f"Model confidence: {confidence:.1%}")


def main():
    texts, labels = load_dataset()

    print(f"Loaded {len(texts)} notifications.")
    print(f"Categories: {sorted(set(labels))}")

    model = train_model(texts, labels)
    test_predictions(model)


if __name__ == "__main__":
    main()
