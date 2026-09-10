import type { ReactNode } from "react";
import { Check } from "lucide-react";
import type { MeetingRating, SkillTreeNode } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";

const ratingOrder: MeetingRating[] = ["green", "yellow", "red"];

function ratingText(skill: SkillTreeNode, rating: MeetingRating): string {
  const text = {
    green: skill.green_text,
    yellow: skill.yellow_text,
    red: skill.red_text,
  }[rating];
  return text.trim() === "" ? "—" : text;
}

const rowToneClass: Record<MeetingRating, string> = {
  green: "border-rating-green/50 bg-accent-50 text-brand-700",
  yellow: "border-rating-yellow/50 bg-amber-50 text-amber-800",
  red: "border-rating-red/50 bg-red-50 text-red-800",
};

const activeRowClass: Record<MeetingRating, string> = {
  green: "border-rating-green ring-2 ring-rating-green",
  yellow: "border-rating-yellow ring-2 ring-rating-yellow",
  red: "border-rating-red ring-2 ring-rating-red",
};

const restBoxClass: Record<MeetingRating, string> = {
  green: "border-rating-green bg-white",
  yellow: "border-rating-yellow bg-white",
  red: "border-rating-red bg-white",
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
    <div className="rounded-xl border border-slate-200 bg-white px-3.5 py-3">
      <div className="mb-2.5 text-sm font-semibold text-ink" id={`focus-${skill.id}`}>
        {skill.name}
      </div>
      <div className="space-y-2" role="radiogroup" aria-labelledby={`focus-${skill.id}`}>
        {ratingOrder.map((value) => {
          const active = rating === value;
          return (
            <button
              key={value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => select(value)}
              className={cn(
                "flex w-full items-center gap-2.5 rounded-lg border px-3 py-2.5 text-start text-sm font-medium transition-all",
                rowToneClass[value],
                active ? activeRowClass[value] : "hover:brightness-95"
              )}
            >
              <span
                className={cn(
                  "flex h-5 w-5 shrink-0 items-center justify-center rounded-md border",
                  active ? activeBoxClass[value] : restBoxClass[value]
                )}
              >
                {active && <Check className="h-3.5 w-3.5" />}
              </span>
              <span className="font-medium">{ratingText(skill, value)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
