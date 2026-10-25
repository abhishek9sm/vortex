import type { Importance, Notification } from "../types";

export const KEYWORD_OVERRIDE_LEVEL: Importance = "HIGH";
const IMPORTANCE_ORDER: Importance[] = ["HIGH", "MEDIUM", "LOW"];

export function getEffectiveImportance(
  notification: Notification,
  keywordOverrideLevel: Importance,
): Importance {
  return notification.keywordOverride
    ? keywordOverrideLevel
    : notification.importance;
}

export function sortNotifications(
  notifications: Notification[],
  selectedLevel: Exclude<Importance, "UNKNOWN">,
  keywordOverrideLevel: Importance,
): Notification[] {
  const selectedOrder = [
    selectedLevel,
    ...IMPORTANCE_ORDER.filter((level) => level !== selectedLevel),
  ];
  const rank = new Map<Importance, number>([
    ...selectedOrder.map((level, index) => [level, index] as const),
    ["UNKNOWN", IMPORTANCE_ORDER.length],
  ]);

  return [...notifications].sort(
    (left, right) =>
      rank.get(getEffectiveImportance(left, keywordOverrideLevel))! -
      rank.get(getEffectiveImportance(right, keywordOverrideLevel))!,
  );
}
