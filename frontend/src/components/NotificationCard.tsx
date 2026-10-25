import { useState } from "react";
import {
  getEffectiveImportance,
  KEYWORD_OVERRIDE_LEVEL,
} from "../utils/sortNotifications";
import type { Category, Importance, Notification } from "../types";
import { CorrectionForm } from "./CorrectionForm";

interface NotificationCardProps {
  notification: Notification;
  onSaveCorrection: (
    id: string,
    category: Category,
    importance: Importance,
  ) => Promise<boolean>;
}

export function NotificationCard({
  notification,
  onSaveCorrection,
}: NotificationCardProps) {
  const [editing, setEditing] = useState(false);
  const effectiveImportance = getEffectiveImportance(
    notification,
    KEYWORD_OVERRIDE_LEVEL,
  );

  return (
    <article className="notification-card">
      <p className="notification-text">{notification.text}</p>
      <div className="notification-meta">
        <span className="badge badge-category">{notification.category}</span>
        <span className={`badge badge-${effectiveImportance}`}>
          {effectiveImportance}
        </span>
        <span className="confidence">
          Confidence <strong>{Math.round(notification.confidence * 100)}%</strong>
        </span>
        {notification.keywordOverride && (
          <span className="badge badge-override">Keyword override</span>
        )}
        {notification.corrected && (
          <span className="corrected-indicator">Corrected</span>
        )}
      </div>
      <p className="explanation">
        <span aria-hidden="true">↳</span> {notification.explanation}
      </p>
      {!editing ? (
        <button
          className="text-button"
          type="button"
          aria-expanded={editing}
          onClick={() => setEditing(true)}
        >
          Correct this <span aria-hidden="true">↗</span>
        </button>
      ) : (
        <CorrectionForm
          initialCategory={notification.category}
          initialImportance={notification.importance}
          onSave={(category, importance) =>
            onSaveCorrection(notification.id, category, importance)
          }
          onCancel={() => setEditing(false)}
        />
      )}
    </article>
  );
}
