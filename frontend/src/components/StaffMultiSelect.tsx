import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import type { StaffMember } from "@/lib/api/types";
import { toggled } from "@/lib/utils/arrays";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/DropdownMenu";

export function StaffMultiSelect({
  candidates,
  selected,
  onChange,
  label,
}: {
  candidates: StaffMember[];
  selected: string[];
  onChange: (selected: string[]) => void;
  label?: string;
}): ReactNode {
  const selectedNames: string = candidates
    .filter((member) => selected.includes(member.id))
    .map((member) => member.full_name)
    .join(", ");

  return (
    <DropdownMenu modal={false}>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label={label}
          className="flex min-h-11 w-full items-center justify-between gap-2 rounded-control border border-slate-300 bg-white px-3.5 py-2 text-start text-sm text-ink shadow-soft transition-colors hover:border-slate-400 focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-400/15"
        >
          <span className={selectedNames ? "" : "text-slate-400"}>
            {selectedNames || "בחירה..."}
          </span>
          <ChevronDown className="h-4 w-4 shrink-0 opacity-60" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="max-h-72 overflow-y-auto">
        {candidates.map((member) => {
          const isSelected: boolean = selected.includes(member.id);
          return (
            <DropdownMenuCheckboxItem
              key={member.id}
              checked={isSelected}
              onSelect={(event) => event.preventDefault()}
              onCheckedChange={(checked) =>
                onChange(toggled(selected, member.id, checked === true))
              }
            >
              {member.full_name}
            </DropdownMenuCheckboxItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
