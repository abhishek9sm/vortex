import { useEffect, useState } from "react";
import { FeedbackPanel } from "./components/FeedbackPanel";
import { KeywordPanel } from "./components/KeywordPanel";
import { NotificationCard } from "./components/NotificationCard";
import { NotificationForm } from "./components/NotificationForm";
import { ReferencePanel } from "./components/ReferencePanel";
import { SortBar } from "./components/SortBar";
import { useNotifications } from "./hooks/useNotifications";
import type { Importance } from "./types";

export default function App() {
  const [theme, setTheme] = useState<"light" | "dark">(() =>
    window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
  );
  const {
    notifications,
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
  } = useNotifications();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  return (
    <main className="app-shell">
      <header className="app-header">
        <a className="brand" href="#" aria-label="BuzzKill home">
          <span className="brand-mark" aria-hidden="true">
            b.
          </span>
          <span>BuzzKill</span>
        </a>
        <div className="header-actions">
          <span className="local-status">
            <span className="status-dot" aria-hidden="true" />
            {serviceReady ? "LOCAL AI CONNECTED" : "LOCAL AI OFFLINE"}
          </span>
          <button
            className="theme-toggle"
            type="button"
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            onClick={() =>
              setTheme((current) => (current === "light" ? "dark" : "light"))
            }
          >
            <span aria-hidden="true">{theme === "light" ? "☾" : "☼"}</span>
            <span>{theme === "light" ? "Dark" : "Light"} mode</span>
          </button>
        </div>
      </header>

      <section className="intro">
        <div>
          <p className="eyebrow">YOUR ATTENTION, BACK IN YOUR HANDS</p>
          <h1>Less noise.<br /><span>More signal.</span></h1>
          <p className="intro-copy">
            A calmer inbox starts with knowing what matters. Sort, prioritize,
            and teach BuzzKill what deserves your attention.
          </p>
        </div>
        <div className="intro-art" aria-hidden="true">
          <span className="orbit orbit-one" />
          <span className="orbit orbit-two" />
          <span className="orbit-core">b</span>
          <span className="orbit-dot dot-one" />
          <span className="orbit-dot dot-two" />
          <span className="orbit-dot dot-three" />
        </div>
      </section>

      {error && (
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      <div className="dashboard-grid">
        <aside className="sidebar">
          <NotificationForm onClassify={classify} loading={loading} />
          <KeywordPanel
            keywords={keywords}
            onAdd={addKeyword}
            onRemove={removeKeyword}
          />
          <FeedbackPanel feedback={feedback} />
        </aside>

        <div className="main-column">
          <section className="panel inbox-panel" aria-labelledby="inbox-title">
            <div className="inbox-heading">
              <div>
                <p className="eyebrow">04 / YOUR INBOX</p>
                <h2 id="inbox-title">
                  Notifications <span className="count">{notifications.length}</span>
                </h2>
              </div>
              <span className="inbox-indicator">
                <span className="status-dot" aria-hidden="true" /> SORTED
              </span>
            </div>
            <SortBar
              selected={sortLevel}
              onChange={(level: Exclude<Importance, "UNKNOWN">) =>
                setSortLevel(level)
              }
            />
            <p className="sort-help">
              Selected importance first · remaining levels in order · UNKNOWN last
            </p>
            <div className="notification-list">
              {notifications.length === 0 ? (
                <p className="empty-state">
                  No classified notifications yet. Add one to see the local
                  model&apos;s result.
                </p>
              ) : (
                notifications.map((notification) => (
                  <NotificationCard
                    key={notification.id}
                    notification={notification}
                    onSaveCorrection={correctNotification}
                  />
                ))
              )}
            </div>
          </section>
          <ReferencePanel />
        </div>
      </div>
      <footer className="app-footer">
        <span>BUZZKILL / LOCAL-FIRST NOTIFICATION SORTER</span>
        <span>BUILT FOR A QUIETER INBOX</span>
      </footer>
    </main>
  );
}
