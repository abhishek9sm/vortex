import { useCallback, useEffect, useMemo, useState } from "react";
import {
  checkService,
  classifyNotification,
  getFeedback,
  getKeywords,
  saveFeedback,
  saveKeywords,
} from "../api";
import type { Category, Feedback, Importance, Notification } from "../types";
import {
  KEYWORD_OVERRIDE_LEVEL,
  sortNotifications,
} from "../utils/sortNotifications";

function matchesKeyword(text: string, keywords: string[]): boolean {
  const normalizedText = text.toLocaleLowerCase();
  return keywords.some((keyword) =>
    normalizedText.includes(keyword.toLocaleLowerCase()),
  );
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [sortLevel, setSortLevel] =
    useState<Exclude<Importance, "UNKNOWN">>("HIGH");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [serviceReady, setServiceReady] = useState(false);

  useEffect(() => {
    let active = true;
    Promise.all([checkService(), getKeywords(), getFeedback()])
      .then(([ready, savedKeywords, savedFeedback]) => {
        if (!active) return;
        setServiceReady(ready);
        setKeywords(savedKeywords);
        setFeedback(savedFeedback);
        setError("");
      })
      .catch((loadError: unknown) => {
        if (!active) return;
        setServiceReady(false);
        setError(
          loadError instanceof Error
            ? loadError.message
            : "The local AI service could not be loaded.",
        );
      });

    return () => {
      active = false;
    };
  }, []);

  const decoratedNotifications = useMemo(
    () =>
      notifications.map((notification) => ({
        ...notification,
        keywordOverride: matchesKeyword(notification.text, keywords),
      })),
    [notifications, keywords],
  );

  const sortedNotifications = useMemo(
    () =>
      sortNotifications(
        decoratedNotifications,
        sortLevel,
        KEYWORD_OVERRIDE_LEVEL,
      ),
    [decoratedNotifications, sortLevel],
  );

  const classify = useCallback(async (text: string) => {
    setLoading(true);
    setError("");
    try {
      const result = await classifyNotification(text.trim());
      setNotifications((current) => [result, ...current]);
      return true;
    } catch (classifyError) {
      setError(
        classifyError instanceof Error
          ? classifyError.message
          : "The notification could not be classified.",
      );
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const addKeyword = useCallback(
    async (keyword: string) => {
      const trimmed = keyword.trim();
      if (!trimmed || keywords.some((item) => item.toLowerCase() === trimmed.toLowerCase())) {
        return false;
      }

      const updated = [...keywords, trimmed];
      try {
        await saveKeywords(updated);
        setKeywords(updated);
        setError("");
        return true;
      } catch (saveError) {
        setError(
          saveError instanceof Error
            ? saveError.message
            : "The keyword could not be saved.",
        );
        return false;
      }
    },
    [keywords],
  );

  const removeKeyword = useCallback(
    async (keyword: string) => {
      const updated = keywords.filter((item) => item !== keyword);
      try {
        await saveKeywords(updated);
        setKeywords(updated);
        setError("");
      } catch (saveError) {
        setError(
          saveError instanceof Error
            ? saveError.message
            : "The keyword could not be removed.",
        );
      }
    },
    [keywords],
  );

  const correctNotification = useCallback(
    async (
      id: string,
      correctedCategory: Category,
      correctedImportance: Importance,
    ) => {
      const notification = notifications.find((item) => item.id === id);
      if (!notification) return false;

      const correction: Feedback = {
        notificationText: notification.text,
        correctedCategory,
        correctedImportance,
      };

      try {
        await saveFeedback(
          correction,
          notification.category,
          notification.importance,
        );
        setNotifications((current) =>
          current.map((item) =>
            item.id === id
              ? {
                  ...item,
                  category: correctedCategory,
                  importance: correctedImportance,
                  corrected: true,
                }
              : item,
          ),
        );
        setFeedback((current) => [...current, correction]);
        setError("");
        return true;
      } catch (saveError) {
        setError(
          saveError instanceof Error
            ? saveError.message
            : "The feedback could not be saved.",
        );
        return false;
      }
    },
    [notifications],
  );

  return {
    notifications: sortedNotifications,
    keywords,
    feedback,
    sortLevel,
    setSortLevel,
    error,
    loading,
    serviceReady,
    classify,
    addKeyword,
    removeKeyword,
    correctNotification,
  };
}
