import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { initials } from "@/lib/utils/initials";

export function StudentLinkCard({
  id,
  name,
  to,
}: {
  id: string;
  name: string;
  to?: string;
}): ReactNode {
  return (
    <Link to={to ?? `/students/${id}`}>
      <Card className="flex items-center gap-3 px-4 py-4 transition-colors hover:border-brand-300 hover:bg-brand-50/40">
        <span
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-50 text-sm font-bold text-brand"
          aria-hidden
        >
          {initials(name)}
        </span>
        <span className="min-w-0 flex-1 truncate font-medium text-ink">{name}</span>
        <ChevronLeft className="h-5 w-5 shrink-0 text-slate-400" />
      </Card>
    </Link>
  );
}
