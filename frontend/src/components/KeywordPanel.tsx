import { useState, type FormEvent } from "react";

interface KeywordPanelProps {
  keywords: string[];
  onAdd: (keyword: string) => Promise<boolean>;
  onRemove: (keyword: string) => void;
}

export function KeywordPanel({ keywords, onAdd, onRemove }: KeywordPanelProps) {
  const [keyword, setKeyword] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (await onAdd(keyword)) setKeyword("");
  }

  return (
    <section className="panel" aria-labelledby="keywords-title">
      <p className="eyebrow">02 / PRIORITY RULES</p>
      <h2 id="keywords-title">Priority keywords</h2>
      <form className="keyword-form" onSubmit={handleSubmit}>
        <label className="visually-hidden" htmlFor="priority-keyword">
          Add a priority keyword
        </label>
        <input
          id="priority-keyword"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          placeholder="Add a keyword"
        />
        <button
          className="button button-secondary"
          type="submit"
          disabled={!keyword.trim()}
        >
          Add
        </button>
      </form>
      <div className="keyword-list" aria-label="Saved priority keywords">
        {keywords.length ? (
          keywords.map((item) => (
            <span className="keyword-chip" key={item}>
              {item}
              <button
                type="button"
                aria-label={`Remove ${item}`}
                onClick={() => onRemove(item)}
              >
                ×
              </button>
            </span>
          ))
        ) : (
          <p className="empty-state">No priority keywords yet.</p>
        )}
      </div>
      <p className="help-text">
        Matches ignore capitalization and raise importance to HIGH.
      </p>
    </section>
  );
}
