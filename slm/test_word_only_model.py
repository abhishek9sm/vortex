
import pandas as pd

from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = Path(__file__).resolve().parent
DATASET_FILE = BASE_DIR / "importance_dataset.csv"


def main():
    df = pd.read_csv(DATASET_FILE)
    df = df.dropna(subset=["text", "importance"]).copy()

    df["text"] = df["text"].astype(str).str.strip()
    df["importance"] = df["importance"].astype(str).str.strip().str.upper()

    df = df[
        (df["text"] != "")
        & df["importance"].isin(["HIGH", "MEDIUM", "LOW"])
    ]
    df = df.drop_duplicates(subset=["text", "importance"])

    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 1),
            max_features=5000,
            sublinear_tf=True
        )),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ])

    model.fit(df["text"], df["importance"])

    tests = [
        "My bank detected a suspicious transaction",
        "My friend sent me a funny video",
        "My assignment deadline is today",
        "A software company offers a discount",
        "Your college event registration is open",
        "You have a new game achievement",
        "My father says there is a family emergency",
        "Your game account has an unfamiliar login",
        "Your software licence expires next month",
        "Your college announced an optional seminar",
        "Your electricity bill payment failed",
        "A creator you follow uploaded a new video"
    ]

    print("WORD-ONLY MODEL: NEW EXAMPLE TEST")
    print("=" * 50)

    for text in tests:
        probabilities = model.predict_proba([text])[0]
        index = probabilities.argmax()

        importance = model.classes_[index]
        confidence = probabilities[index]

        print(f"\nNotification: {text}")
        print(f"Predicted importance: {importance}")
        print(f"Confidence: {confidence:.2%}")


if __name__ == "__main__":
    main()
