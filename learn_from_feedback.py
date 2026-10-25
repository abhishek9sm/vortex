
import csv
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent

DATASET_FILE = BASE_DIR / "notifications.csv"
FEEDBACK_FILE = BASE_DIR / "feedback.csv"
OUTPUT_FILE = BASE_DIR / "personalized_model.joblib"

VALID_CATEGORIES = {
    "Education", "Security", "Personal", "Shopping", "Promotion"
}


def load_original_data():
    df = pd.read_csv(DATASET_FILE)

    required = {"text", "category"}
    if not required.issubset(df.columns):
        raise ValueError(
            "notifications.csv must contain text and category columns."
        )

    df = df[["text", "category"]].dropna()
    df["text"] = df["text"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()

    return df[df["category"].isin(VALID_CATEGORIES)]


def load_feedback():
    if not FEEDBACK_FILE.exists():
        return pd.DataFrame(columns=["text", "category"])

    rows = []

    with open(FEEDBACK_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            text = (row.get("notification_text") or "").strip()
            category = (row.get("corrected_category") or "").strip()

            if text and category in VALID_CATEGORIES:
                rows.append({
                    "text": text,
                    "category": category
                })

    return pd.DataFrame(rows, columns=["text", "category"])


def main():
    original = load_original_data()
    feedback = load_feedback()

    if original.empty:
        print("The original dataset has no valid examples.")
        return

    if feedback.empty:
        print("No valid feedback found.")
        print("Correct some predictions before training.")
        return

    # Give user-confirmed corrections more influence.
    training_data = pd.concat(
        [original, feedback, feedback, feedback],
        ignore_index=True
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000
        )),
        ("classifier", LogisticRegression(max_iter=1000))
    ])

    model.fit(
        training_data["text"],
        training_data["category"]
    )

    joblib.dump(model, OUTPUT_FILE)

    print("Personalized model trained successfully.")
    print("Original examples:", len(original))
    print("Valid feedback examples:", len(feedback))
    print("Total training examples:", len(training_data))
    print("Saved to:", OUTPUT_FILE)
    print("The original model was not changed.")


if __name__ == "__main__":
    main()
