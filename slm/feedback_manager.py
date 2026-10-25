
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
FEEDBACK_FILE = BASE_DIR / "feedback.csv"

CATEGORIES = [
    "Education",
    "Security",
    "Personal",
    "Shopping",
    "Promotion",
]

IMPORTANCE_LEVELS = ["HIGH", "MEDIUM", "LOW"]

def save_feedback(
    text,
    predicted_category,
    corrected_category,
    predicted_importance,
    corrected_importance,
):
    file_exists = FEEDBACK_FILE.exists() and FEEDBACK_FILE.stat().st_size > 0

    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "notification_text",
                "predicted_category",
                "corrected_category",
                "predicted_importance",
                "corrected_importance",
                "timestamp",
            ])

        writer.writerow([
            text,
            predicted_category,
            corrected_category,
            predicted_importance,
            corrected_importance,
            datetime.now().isoformat(timespec="seconds"),
        ])

    print("Feedback saved locally in feedback.csv")


def main():
    from notification_agent import process_notification

    print("=== Notification Sorter Feedback ===")
    text = input("Enter a sample notification: ").strip()

    if not text:
        print("Notification cannot be empty.")
        return

    result = process_notification(text)

    print("\nAI prediction:")
    print("Category:", result["category"])
    print("Importance:", result["importance"])
    print("Reason:", result["reason"])

    answer = input("\nIs this prediction correct? (yes/no): ").strip().lower()

    if answer == "yes":
        print("No correction needed.")
        return

    if answer != "no":
        print("Please enter yes or no.")
        return

    print("\nCategories:", ", ".join(CATEGORIES))
    category = input("Enter the correct category: ").strip().title()

    if category not in CATEGORIES:
        print("Invalid category.")
        return

    print("Importance levels:", ", ".join(IMPORTANCE_LEVELS))
    importance = input("Enter the correct importance: ").strip().upper()

    if importance not in IMPORTANCE_LEVELS:
        print("Invalid importance level.")
        return

    save_feedback(
        text=text,
        predicted_category=result["category"],
        corrected_category=category,
        predicted_importance=result["importance"],
        corrected_importance=importance,
    )


if __name__ == "__main__":
    main()
