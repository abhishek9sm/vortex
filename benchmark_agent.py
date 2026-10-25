
import csv
import statistics
import time
import tracemalloc
from pathlib import Path

from notification_agent import process_notification

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "notifications.csv"

# Repeat the dataset to measure many processing operations.
REPEATS = 10


def load_notifications():
    with open(DATASET_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [
            row["text"].strip()
            for row in reader
            if row.get("text", "").strip()
        ]


def percentile(values, percent):
    ordered = sorted(values)
    index = max(0, int((percent / 100) * len(ordered) + 0.999999) - 1)
    return ordered[min(index, len(ordered) - 1)]


def main():
    notifications = load_notifications()

    if not notifications:
        print("No notifications found in notifications.csv")
        return

    # Warm up the model and Python runtime.
    for text in notifications[:5]:
        process_notification(text)

    timings_ms = []
    fallback_count = 0
    ai_count = 0
    rule_count = 0

    tracemalloc.start()

    for _ in range(REPEATS):
        for text in notifications:
            start = time.perf_counter_ns()
            result = process_notification(text)
            elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000

            timings_ms.append(elapsed_ms)

            if result["source"] == "Priority rules":
                rule_count += 1
            elif result["source"] == "Local AI":
                ai_count += 1
            elif result["source"] == "Local AI + fallback":
                ai_count += 1
                fallback_count += 1

    current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("\n--- Notification Agent Benchmark ---")
    print(f"Notifications processed: {len(timings_ms)}")
    print(f"Rule-based decisions: {rule_count}")
    print(f"AI decisions: {ai_count}")
    print(f"Low-confidence fallbacks: {fallback_count}")

    print("\n--- Latency ---")
    print(f"Average: {statistics.mean(timings_ms):.3f} ms")
    print(f"Median (p50): {statistics.median(timings_ms):.3f} ms")
    print(f"95th percentile: {percentile(timings_ms, 95):.3f} ms")
    print(f"Maximum observed: {max(timings_ms):.3f} ms")

    print("\n--- Python Memory Tracking ---")
    print(f"Current tracked memory: {current_bytes / 1024:.1f} KB")
    print(f"Peak tracked memory: {peak_bytes / 1024:.1f} KB")

    print("\n--- Two-second target ---")
    if max(timings_ms) < 2000:
        print("PASS: Every measured call finished under 2000 ms.")
    else:
        print("FAIL: At least one call took 2000 ms or longer.")

    print(
        "Note: This measures the Python prototype, not the complete "
        "Android notification pipeline or total process RAM."
    )


if __name__ == "__main__":
    main()
