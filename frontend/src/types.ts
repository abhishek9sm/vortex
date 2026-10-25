export const CATEGORIES = [
  "Education",
  "Security",
  "Personal",
  "Shopping",
  "Promotion",
  "UNKNOWN",
] as const;

export const IMPORTANCE_LEVELS = [
  "HIGH",
  "MEDIUM",
  "LOW",
  "UNKNOWN",
] as const;

export type Category = (typeof CATEGORIES)[number];
export type Importance = (typeof IMPORTANCE_LEVELS)[number];

export interface Notification {
  id: string;
  text: string;
  category: Category;
  importance: Importance;
  confidence: number;
  explanation: string;
  keywordOverride: boolean;
  corrected: boolean;
}

export interface Feedback {
  notificationText: string;
  correctedCategory: Category;
  correctedImportance: Importance;
}
