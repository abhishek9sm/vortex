import type { Importance } from "../types";

type SortLevel = Exclude<Importance, "UNKNOWN">;

interface SortBarProps {
  selected: SortLevel;
  onChange: (level: SortLevel) => void;
}

const SORT_OPTIONS: Array<{ label: string; value: SortLevel }> = [
  { label: "High", value: "HIGH" },
  { label: "Medium", value: "MEDIUM" },
  { label: "Low", value: "LOW" },
];

export function SortBar({ selected, onChange }: SortBarProps) {
  return (
    <div className="sort-bar">
      <span className="sort-label">SORT</span>
      <div className="sort-options" role="group" aria-label="Sort by importance">
        {SORT_OPTIONS.map(({ label, value }) => (
          <button
            className="sort-button"
            key={value}
            type="button"
            aria-pressed={selected === value}
            onClick={() => onChange(value)}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
