import { useState, type FormEvent } from "react";
import {
  CATEGORIES,
  IMPORTANCE_LEVELS,
  type Category,
  type Importance,
} from "../types";

interface CorrectionFormProps {
  initialCategory: Category;
  initialImportance: Importance;
  onSave: (category: Category, importance: Importance) => Promise<boolean>;
  onCancel: () => void;
}

export function CorrectionForm({
  initialCategory,
  initialImportance,
  onSave,
  onCancel,
}: CorrectionFormProps) {
  const [category, setCategory] = useState<Category>(initialCategory);
  const [importance, setImportance] = useState<Importance>(initialImportance);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    if (await onSave(category, importance)) onCancel();
    setSaving(false);
  }

  return (
    <form className="correction-form" onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="correct-category">Category</label>
        <select
          id="correct-category"
          value={category}
          onChange={(event) => setCategory(event.target.value as Category)}
        >
          {CATEGORIES.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="correct-importance">Importance</label>
        <select
          id="correct-importance"
          value={importance}
          onChange={(event) => setImportance(event.target.value as Importance)}
        >
          {IMPORTANCE_LEVELS.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </div>
      <div className="button-row correction-actions">
        <button className="button button-primary" type="submit" disabled={saving}>
          {saving ? "Saving…" : "Save feedback"}
        </button>
        <button className="button button-secondary" type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}
