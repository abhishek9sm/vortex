
import pandas as pd
import joblib

from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

BASE_DIR = Path(__file__).resolve().parent
DATASET_FILE = BASE_DIR / "importance_dataset.csv"
MODEL_FILE = BASE_DIR / "importance_model.joblib"

LABELS = ["HIGH", "MEDIUM", "LOW"]

# 1. Load and validate data
df = pd.read_csv(DATASET_FILE)

if not {"text", "importance"}.issubset(df.columns):
    raise ValueError("CSV must contain text and importance columns.")

df = df.dropna(subset=["text", "importance"]).copy()
df["text"] = df["text"].astype(str).str.strip()
df["importance"] = df["importance"].astype(str).str.strip().str.upper()

df = df[
    (df["text"] != "")
    & df["importance"].isin(LABELS)
].copy()

# Remove repeated text, even if it has conflicting labels.
# Conflicting labels are reported so they can be reviewed.
conflicts = df.groupby("text")["importance"].nunique()
conflict_texts = conflicts[conflicts > 1].index

if len(conflict_texts):
    print("\nWARNING: Conflicting labels found for:")
    for text in conflict_texts:
        print("-", text)
    print("Review these rows in the CSV before relying on results.")

df = df.drop_duplicates(subset=["text"], keep="first")

if df["importance"].nunique() != 3:
    raise ValueError("Dataset must contain HIGH, MEDIUM and LOW.")

counts = df["importance"].value_counts()
if counts.min() < 5:
    raise ValueError(
        "Each importance class needs at least 5 examples for 5-fold CV."
    )

X = df["text"]
y = df["importance"]

print("Unique examples:", len(df))
print("\nLabel counts:")
print(y.value_counts())

# 2. Create the lightweight classifier
def create_model():
    return Pipeline([
        (
            "tfidf",
            
TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)

        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced"
            )
        )
    ])

# 3. Evaluate using stratified 5-fold cross-validation
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

evaluation_model = create_model()

predictions = cross_val_predict(
    evaluation_model,
    X,
    y,
    cv=cv,
    method="predict"
)

probabilities = cross_val_predict(
    evaluation_model,
    X,
    y,
    cv=cv,
    method="predict_proba"
)

# The probability columns follow the classifier's class order.
classes = evaluation_model.fit(X, y).named_steps["classifier"].classes_
confidence = probabilities.max(axis=1)

print("\n" + "=" * 50)
print("5-FOLD CROSS-VALIDATION RESULTS")
print("=" * 50)

print(f"\nCross-validation accuracy: {accuracy_score(y, predictions) * 100:.2f}%")
print(f"Macro F1 score: {f1_score(y, predictions, average='macro', zero_division=0):.3f}")

print("\nClassification report:")
print(classification_report(
    y,
    predictions,
    labels=LABELS,
    zero_division=0
))

print("Confusion matrix (rows=actual, columns=predicted):")
print(confusion_matrix(y, predictions, labels=LABELS))
print("Label order:", LABELS)

print("\nCross-validated confidence summary:")
print(f"Mean maximum confidence: {confidence.mean():.3f}")
print(f"Median maximum confidence: {pd.Series(confidence).median():.3f}")
print("Reminder: confidence scores are not guaranteed to be calibrated.")

print("\nCross-validated predictions:")
for text, actual, predicted, score in zip(
    X, y, predictions, confidence
):
    result = "CORRECT" if actual == predicted else "WRONG"
    print(
        f"{result:7} | actual={actual:6} | "
        f"predicted={predicted:6} | confidence={score:.3f} | {text}"
    )

# 4. Train final model on all available examples
final_model = create_model()
final_model.fit(X, y)
joblib.dump(final_model, MODEL_FILE)

print("\n" + "=" * 50)
print("FINAL MODEL SAVED")
print("=" * 50)
print("Model:", MODEL_FILE)
print("Training examples:", len(X))
print("This final model was trained on all examples.")
print("Cross-validation results above estimate performance on unseen data.")
