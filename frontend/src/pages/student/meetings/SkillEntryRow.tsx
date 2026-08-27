import type { ReactNode } from "react";
import type { MeetingRating, SkillTreeNode } from "@/lib/api/types";
import type { EntryDraft } from "@/lib/meetings/buildEntries";
import { ratingLabels } from "@/lib/utils/hebrew";
import { cn } from "@/lib/utils/cn";

const ratingOrder: MeetingRating[] = ["green", "yellow", "red"];

const ratingButtonClass: Record<MeetingRating, string> = {
  green: "data-[active=true]:bg-rating-green data-[active=true]:text-white",
  yellow: "data-[active=true]:bg-rating-yellow data-[active=true]:text-white",
  red: "data-[active=true]:bg-rating-red data-[active=true]:text-white",
};

export function SkillEntryRow({
  skill,
  draft,
  onChange,
}: {
  skill: SkillTreeNode;
  draft: EntryDraft | null;
  onChange: (next: EntryDraft | null) => void;
}): ReactNode {
  const rating = draft?.rating ?? null;
  const solutionIds = draft?.solutionIds ?? [];
  const showSolutions = rating === "yellow" || rating === "red";

  function selectRating(next: MeetingRating): void {
    if (rating === next) {
      onChange(null);
      return;
    }
    onChange({ rating: next, solutionIds: next === "green" ? [] : solutionIds });
  }

  function toggleSolution(solutionId: string): void {
    const nextIds = solutionIds.includes(solutionId)
      ? solutionIds.filter((id) => id !== solutionId)
      : [...solutionIds, solutionId];
    onChange({ rating, solutionIds: nextIds });
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm text-ink">{skill.name}</span>
        <div className="flex gap-1">
          {ratingOrder.map((value) => (
            <button
              key={value}
              type="button"
              data-active={rating === value}
              onClick={() => selectRating(value)}
              className={cn(
                "rounded-md border border-slate-200 px-2.5 py-1 text-xs font-medium text-ink-muted transition-colors hover:bg-slate-50",
                ratingButtonClass[value]
              )}
            >
              {ratingLabels[value]}
            </button>
          ))}
        </div>
      </div>

      {showSolutions && (
        <div className="mt-2 border-t border-slate-100 pt-2">
          {skill.solutions.length === 0 ? (
            <p className="text-xs text-ink-muted">אין פתרונות מוגדרים לכישור זה.</p>
          ) : (
            <div className="space-y-1">
              <div className="text-xs font-medium text-ink-muted">פתרונות:</div>
              {skill.solutions.map((solution) => (
                <label
                  key={solution.id}
                  className="flex items-center gap-2 text-sm text-ink"
                >
                  <input
                    type="checkbox"
                    checked={solutionIds.includes(solution.id)}
                    onChange={() => toggleSolution(solution.id)}
                    className="h-4 w-4 accent-brand"
                  />
                  {solution.text}
                </label>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
