
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
model = joblib.load(BASE_DIR / "importance_model.joblib")

tests = [
    "My bank detected a suspicious transaction",
    "My friend sent me a funny video",
    "My assignment deadline is today",
    "A software company offers a discount",
    "Your college event registration is open",
    "You have a new game achievement"
]

for text in tests:
    probabilities = model.predict_proba([text])[0]
    index = probabilities.argmax()

    importance = model.classes_[index]
    confidence = probabilities[index]

    print(f"\nNotification: {text}")
    print(f"Predicted importance: {importance}")
    print(f"Model confidence: {confidence:.2%}")
