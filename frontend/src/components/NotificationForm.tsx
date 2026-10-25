import { useState, type FormEvent } from "react";

interface NotificationFormProps {
  onClassify: (text: string) => Promise<boolean>;
  loading: boolean;
}

export function NotificationForm({
  onClassify,
  loading,
}: NotificationFormProps) {
  const [text, setText] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!text.trim()) return;
    if (await onClassify(text)) setText("");
  }

  return (
    <section className="panel" aria-labelledby="new-notification-title">
      <p className="eyebrow">01 / INBOX</p>
      <h2 id="new-notification-title">New notification</h2>
      <form onSubmit={handleSubmit}>
        <label htmlFor="notification-text">Notification text</label>
        <textarea
          id="notification-text"
          placeholder="Paste or type a notification…"
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={4}
        />
        <div className="button-row">
          <button className="button button-primary" type="submit" disabled={loading || !text.trim()}>
            {loading ? "Classifying…" : "Classify"}
          </button>
          <button
            className="button button-secondary"
            type="button"
            onClick={() => setText("")}
          >
            Clear
          </button>
        </div>
      </form>
      <p className="help-text">
        Classification runs through the local Python model service.
      </p>
    </section>
  );
}
