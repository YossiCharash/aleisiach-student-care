import type { ReactNode } from "react";
import { Check } from "lucide-react";
import type { MeetingRating, SkillTreeNode } from "@/lib/api/types";
import { ratingLabels } from "@/lib/utils/hebrew";
import { cn } from "@/lib/utils/cn";

const ratingOrder: MeetingRating[] = ["green", "yellow", "red"];

const activeRowClass: Record<MeetingRating, string> = {
  green: "border-rating-green bg-accent-50 text-brand-700",
  yellow: "border-rating-yellow bg-amber-50 text-amber-800",
  red: "border-rating-red bg-red-50 text-red-800",
};

const activeBoxClass: Record<MeetingRating, string> = {
  green: "border-rating-green bg-rating-green text-white",
  yellow: "border-rating-yellow bg-rating-yellow text-white",
  red: "border-rating-red bg-rating-red text-white",
};

export function FocusRatingRow({
  skill,
  rating,
  onChange,
}: {
  skill: SkillTreeNode;
  rating: MeetingRating | null;
  onChange: (next: MeetingRating | null) => void;
}): ReactNode {
  function select(next: MeetingRating): void {
    onChange(rating === next ? null : next);
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2">
      <div className="mb-2 text-sm font-medium text-ink">{skill.name}</div>
      <div className="space-y-1.5">
        {ratingOrder.map((value) => {
          const active = rating === value;
          return (
            <button
              key={value}
              type="button"
              role="checkbox"
              aria-checked={active}
              onClick={() => select(value)}
              className={cn(
                "flex w-full items-center gap-2 rounded-md border px-3 py-2 text-sm transition-colors",
                active
                  ? activeRowClass[value]
                  : "border-slate-200 text-ink-muted hover:bg-slate-50"
              )}
            >
              <span
                className={cn(
                  "flex h-5 w-5 items-center justify-center rounded border",
                  active ? activeBoxClass[value] : "border-slate-300 bg-white"
                )}
              >
                {active && <Check className="h-3.5 w-3.5" />}
              </span>
              <span className="font-medium">{ratingLabels[value]}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
