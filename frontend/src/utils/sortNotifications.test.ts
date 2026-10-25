import { describe, expect, it } from "vitest";
import type { Notification } from "../types";
import { sortNotifications } from "./sortNotifications";

function item(id: string, importance: Notification["importance"]): Notification {
  return {
    id,
    text: id,
    category: "Personal",
    importance,
    confidence: 0.8,
    explanation: "Test item.",
    keywordOverride: false,
    corrected: false,
  };
}

describe("sortNotifications", () => {
  const notifications = [
    item("low", "LOW"),
    item("unknown", "UNKNOWN"),
    item("high", "HIGH"),
    item("medium", "MEDIUM"),
  ];

  it("places the selected level first, then the default order, with UNKNOWN last", () => {
    expect(
      sortNotifications(notifications, "MEDIUM", "HIGH").map(({ id }) => id),
    ).toEqual(["medium", "high", "low", "unknown"]);
  });

  it("sorts keyword overrides according to their effective importance", () => {
    const overridden = { ...item("urgent low", "LOW"), keywordOverride: true };
    expect(
      sortNotifications([item("medium", "MEDIUM"), overridden], "HIGH", "HIGH").map(
        ({ id }) => id,
      ),
    ).toEqual(["urgent low", "medium"]);
  });

  it("does not mutate the supplied list", () => {
    const input = [...notifications];
    sortNotifications(input, "LOW", "HIGH");
    expect(input.map(({ id }) => id)).toEqual([
      "low",
      "unknown",
      "high",
      "medium",
    ]);
  });
});
