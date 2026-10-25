import type { Category, Feedback, Importance, Notification } from "./types";

interface ApiNotification {
  id: string;
  text: string;
  category: Category;
  importance: Importance;
  confidence: number;
  explanation: string;
  keywordOverride: boolean;
  corrected: boolean;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      ...init,
      headers: {
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...init?.headers,
      },
    });
  } catch (error) {
    console.error("BuzzKill could not reach the local AI service.", error);
    throw new Error(
      "The local AI service is unavailable. Start it with `python slm/local_api.py`.",
    );
  }

  const payload = (await response.json().catch(() => null)) as
    | { error?: string }
    | T
    | null;
  if (!response.ok) {
    const message =
      payload !== null &&
      typeof payload === "object" &&
      "error" in payload &&
      typeof payload.error === "string"
        ? payload.error
        : `Local AI service returned HTTP ${response.status}.`;
    throw new Error(message);
  }
  if (payload === null) {
    throw new Error("The local AI service returned an invalid response.");
  }
  return payload as T;
}

export async function checkService(): Promise<boolean> {
  const result = await request<{ status: string }>("/api/health");
  return result.status === "ok";
}

export async function classifyNotification(text: string): Promise<Notification> {
  return request<ApiNotification>("/api/classify", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export async function saveFeedback(
  feedback: Feedback,
  predictedCategory: Category,
  predictedImportance: Importance,
): Promise<void> {
  await request<{ saved: boolean }>("/api/feedback", {
    method: "POST",
    body: JSON.stringify({
      ...feedback,
      predictedCategory,
      predictedImportance,
    }),
  });
}

export async function getFeedback(): Promise<Feedback[]> {
  const result = await request<{ feedback: Feedback[] }>("/api/feedback");
  return result.feedback;
}

export async function getKeywords(): Promise<string[]> {
  const result = await request<{ keywords: string[] }>("/api/keywords");
  return result.keywords;
}

export async function saveKeywords(keywords: string[]): Promise<void> {
  await request<{ saved: boolean }>("/api/keywords", {
    method: "PUT",
    body: JSON.stringify({ keywords }),
  });
}

export type { Category, Importance };
