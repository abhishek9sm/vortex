
from pathlib import Path
import json
import joblib

# --------------------------------------------------
# 1. FILE PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "notification_model.joblib"
PERSONALIZED_MODEL_PATH = BASE_DIR / "personalized_model.joblib"
IMPORTANCE_MODEL_PATH = BASE_DIR / "importance_model.joblib"
PREFERENCES_PATH = BASE_DIR / "user_preferences.json"


# --------------------------------------------------
# 2. LOAD CATEGORY MODEL
# --------------------------------------------------

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        "Category model not found. Run train_classifier.py first."
    )

base_model = joblib.load(MODEL_PATH)

if PERSONALIZED_MODEL_PATH.exists():
    category_model = joblib.load(PERSONALIZED_MODEL_PATH)
    CATEGORY_MODEL_NAME = "Personalized category AI"
else:
    category_model = base_model
    CATEGORY_MODEL_NAME = "Base category AI"


# --------------------------------------------------
# 3. LOAD IMPORTANCE MODEL
# --------------------------------------------------

if not IMPORTANCE_MODEL_PATH.exists():
    raise FileNotFoundError(
        "Importance model not found. "
        "Run train_importance_model.py first."
    )

importance_model = joblib.load(IMPORTANCE_MODEL_PATH)
IMPORTANCE_MODEL_NAME = "Local importance AI"


# --------------------------------------------------
# 4. CONFIDENCE SETTINGS
# --------------------------------------------------

# Provisional thresholds, not calibrated guarantees.
IMPORTANCE_CONFIDENCE_THRESHOLD = 0.45
IMPORTANCE_MIN_MARGIN = 0.08


# --------------------------------------------------
# 5. LOAD USER PREFERENCES
# --------------------------------------------------

def load_user_preferences():
    """Load and validate user-editable priorities."""

    if not PREFERENCES_PATH.exists():
        raise FileNotFoundError(
            "user_preferences.json was not found."
        )

    try:
        with open(PREFERENCES_PATH, "r", encoding="utf-8") as file:
            preferences = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            "user_preferences.json contains invalid JSON."
        ) from error

    if not isinstance(preferences, dict):
        raise ValueError("Preferences must be a JSON object.")

    priorities = preferences.get("priorities")

    if not isinstance(priorities, dict):
        raise ValueError(
            "The preferences file must contain a priorities object."
        )

    for level in ["HIGH", "MEDIUM", "LOW"]:
        keywords = priorities.get(level, [])

        if not isinstance(keywords, list) or not all(
            isinstance(word, str) for word in keywords
        ):
            raise ValueError(
                f"Priority '{level}' must contain a list of strings."
            )

    return preferences


# --------------------------------------------------
# 6. CHECK USER-DEFINED PRIORITIES
# --------------------------------------------------

def check_user_priorities(text):
    """Apply explicit user rules before AI predictions."""

    preferences = load_user_preferences()
    priorities = preferences.get("priorities", {})

    normalized_text = text.casefold()

    # HIGH takes precedence over MEDIUM, then LOW.
    for level in ["HIGH", "MEDIUM", "LOW"]:
        for keyword in priorities.get(level, []):
            keyword = keyword.strip()

            if keyword and keyword.casefold() in normalized_text:
                return {
                    "importance": level,
                    "reason": f"Matched user priority: {keyword}"
                }

    return None


# --------------------------------------------------
# 7. PREDICT CATEGORY
# --------------------------------------------------

def classify_category(text):
    """Return the predicted category and its model score."""

    probabilities = category_model.predict_proba([text])[0]
    best_index = probabilities.argmax()

    category = str(category_model.classes_[best_index])
    confidence = float(probabilities[best_index])

    return category, confidence


# --------------------------------------------------
# 8. PREDICT IMPORTANCE
# --------------------------------------------------

def classify_importance(text):
    """Return importance, top score, and top-two score margin."""

    probabilities = importance_model.predict_proba([text])[0]
    classes = importance_model.classes_

    best_index = probabilities.argmax()
    importance = str(classes[best_index])
    confidence = float(probabilities[best_index])

    sorted_probabilities = sorted(
        (float(value) for value in probabilities),
        reverse=True
    )

    if len(sorted_probabilities) >= 2:
        margin = sorted_probabilities[0] - sorted_probabilities[1]
    else:
        margin = confidence

    return importance, confidence, margin


# --------------------------------------------------
# 9. PROCESS A NOTIFICATION
# --------------------------------------------------

def process_notification(text):
    """
    Apply user rules first, then category and importance AI.

    Return a dictionary suitable for later integration.
    """

    if not isinstance(text, str) or not text.strip():
        return {
            "category": "Unknown",
            "importance": "UNKNOWN",
            "source": "Fallback",
            "confidence": None,
            "category_confidence": None,
            "reason": "Notification content is empty or invalid."
        }

    text = text.strip()

    # Step 1: Explicit user priorities take precedence.
    priority = check_user_priorities(text)

    # Step 2: Predict category independently.
    category, category_confidence = classify_category(text)

    if priority is not None:
        return {
            "category": category,
            "importance": priority["importance"],
            "source": "User priority rules",
            "confidence": None,
            "category_confidence": round(category_confidence, 3),
            "reason": priority["reason"]
        }

    # Step 3: Predict importance independently.
    importance, confidence, margin = classify_importance(text)

    # Step 4: Avoid presenting uncertain predictions as decisions.
    if (
        confidence < IMPORTANCE_CONFIDENCE_THRESHOLD
        or margin < IMPORTANCE_MIN_MARGIN
    ):
        return {
            "category": category,
            "importance": "UNKNOWN",
            "source": IMPORTANCE_MODEL_NAME,
            "confidence": round(confidence, 3),
            "category_confidence": round(category_confidence, 3),
            "reason": (
                "Importance prediction is uncertain. "
                "The confidence or gap between the top two "
                "scores is below the prototype threshold."
            )
        }

    # Step 5: Return the accepted AI prediction.
    return {
        "category": category,
        "importance": importance,
        "source": IMPORTANCE_MODEL_NAME,
        "confidence": round(confidence, 3),
        "category_confidence": round(category_confidence, 3),
        "reason": "Importance predicted by the local classifier."
    }


# --------------------------------------------------
# 10. INTERACTIVE TESTING
# --------------------------------------------------

def main():
    print("Local Notification Agent")
    print(f"Category model: {CATEGORY_MODEL_NAME}")
    print(f"Importance model: {IMPORTANCE_MODEL_NAME}")
    print("User preferences are loaded from JSON.")
    print("Type a notification to analyze it.")
    print("Type 'exit' to stop.\n")

    while True:
        try:
            text = input("Notification: ")

            if text.strip().casefold() == "exit":
                break

            result = process_notification(text)

            print("\nAgent decision:")

            for key, value in result.items():
                print(f"{key}: {value}")

            print()

        except (FileNotFoundError, ValueError) as error:
            print(f"Configuration error: {error}")
            print("Check your model files and user_preferences.json.\n")


if __name__ == "__main__":
    main()
