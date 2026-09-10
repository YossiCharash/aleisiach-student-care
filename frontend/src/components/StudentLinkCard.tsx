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
    <Link to={to ?? `/students/${id}`} className="group block">
      <Card className="flex items-center gap-3 px-4 py-4 transition-all duration-150 group-hover:-translate-y-0.5 group-hover:border-brand-300 group-hover:shadow-lift">
        <span
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-soft text-sm font-bold text-brand-700 ring-1 ring-brand-100 transition-colors group-hover:bg-brand group-hover:text-white group-hover:ring-brand"
          aria-hidden
        >
          {initials(name)}
        </span>
        <span className="min-w-0 flex-1 truncate font-semibold text-ink">{name}</span>
        <ChevronLeft className="h-5 w-5 shrink-0 text-slate-400 transition-all group-hover:-translate-x-0.5 group-hover:text-brand" />
      </Card>
    </Link>
  );
}
