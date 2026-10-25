
import csv
from collections import Counter
from pathlib import Path

path = Path(__file__).resolve().parent / "notifications.csv"

with open(path, "r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

texts = [row["text"].strip().lower() for row in rows]
labels = [row["category"].strip() for row in rows]

print("Total examples:", len(rows))
print("\nExamples per category:")

for category, count in sorted(Counter(labels).items()):
    print(f"{category}: {count}")

print("\nDuplicate notification texts:")
duplicates = [text for text, count in Counter(texts).items()
              if count > 1]

if duplicates:
    for text in duplicates:
        print("-", text)
else:
    print("None")

print("\nMissing fields:")
missing = [
    i + 2 for i, row in enumerate(rows)
    if not row.get("text", "").strip()
    or not row.get("category", "").strip()
]

print(missing if missing else "None")

