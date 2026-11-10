import type { ReactNode } from "react";
import type { StaffMember } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";
import { toggled } from "@/lib/utils/arrays";

export function StaffChipPicker({
  candidates,
  selected,
  onChange,
  memberLabel,
}: {
  candidates: StaffMember[];
  selected: string[];
  onChange: (selected: string[]) => void;
  memberLabel?: (member: StaffMember) => string;
}): ReactNode {
  return (
    <div className="flex flex-wrap gap-1.5">
      {candidates.map((member) => {
        const isSelected = selected.includes(member.id);
        return (
          <button
            key={member.id}
            type="button"
            aria-pressed={isSelected}
            aria-label={memberLabel?.(member)}
            onClick={() => onChange(toggled(selected, member.id, !isSelected))}
            className={cn(
              "rounded-full border px-2.5 py-0.5 text-xs transition-colors",
              isSelected
                ? "border-brand-500 bg-brand-500 text-white"
                : "border-slate-200 bg-white text-ink-muted hover:border-brand-300 hover:text-ink"
            )}
          >
            {member.full_name}
          </button>
        );
      })}
    </div>
  );
}
