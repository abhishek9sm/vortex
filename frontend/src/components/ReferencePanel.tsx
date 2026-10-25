import { CATEGORIES, IMPORTANCE_LEVELS } from "../types";

export function ReferencePanel() {
  return (
    <section className="panel reference-panel" aria-labelledby="reference-title">
      <p className="eyebrow">QUICK REFERENCE</p>
      <h2 id="reference-title">Sorting vocabulary</h2>
      <div className="reference-row">
        <span className="reference-label">Categories</span>
        <div className="reference-values">
          {CATEGORIES.map((category) => (
            <span className="badge badge-category" key={category}>
              {category}
            </span>
          ))}
        </div>
      </div>
      <div className="reference-row">
        <span className="reference-label">Importance</span>
        <div className="reference-values">
          {IMPORTANCE_LEVELS.map((importance) => (
            <span className={`badge badge-${importance}`} key={importance}>
              {importance}
            </span>
          ))}
        </div>
      </div>
      <p className="help-text">
        UNKNOWN is shown when a prediction is uncertain.
      </p>
    </section>
  );
}
