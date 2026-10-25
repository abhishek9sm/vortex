
import pandas as pd

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = Path(__file__).resolve().parent

df = pd.read_csv(BASE_DIR / "importance_dataset.csv")
df = df.dropna(subset=["text", "importance"]).copy()

df["text"] = df["text"].astype(str).str.strip()
df["importance"] = (
    df["importance"].astype(str).str.strip().str.upper()
)

df = df[
    (df["text"] != "")
    & df["importance"].isin(["HIGH", "MEDIUM", "LOW"])
]
df = df.drop_duplicates(subset=["text", "importance"])

X_train, X_test, y_train, y_test = train_test_split(
    df["text"],
    df["importance"],
    test_size=0.25,
    random_state=42,
    stratify=df["importance"]
)

models = {
    "Current model": Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000
        )),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ))
    ]),

    "Unweighted model": Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000
        )),
        ("classifier", LogisticRegression(
            max_iter=1000
        ))
    ]),

    "Word-only model": Pipeline([
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
}

for name, model in models.items():
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("\n" + "=" * 45)
    print(name)
    print("=" * 45)

    print(
        "Accuracy:",
        round(accuracy_score(y_test, predictions) * 100, 2),
        "%"
    )

    print(classification_report(
        y_test,
        predictions,
        labels=["HIGH", "MEDIUM", "LOW"],
        zero_division=0
    ))

