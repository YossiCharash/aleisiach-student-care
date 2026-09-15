import type { CSSProperties, ReactNode } from "react";
import { Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils/cn";
import { initials } from "@/lib/utils/initials";

export function StudentLinkCard({
  id,
  name,
  to,
  color,
}: {
  id: string;
  name: string;
  to?: string;
  color?: string;
}): ReactNode {
  const accentStyle = color
    ? ({
        "--wc": color,
        "--wc-soft": `${color}1a`,
        "--wc-ring": `${color}33`,
      } as CSSProperties)
    : undefined;

  return (
    <Link to={to ?? `/students/${id}`} className="group block" style={accentStyle}>
      <Card
        className={cn(
          "flex items-center gap-3 px-4 py-4 transition-all duration-150 group-hover:-translate-y-0.5 group-hover:shadow-lift",
          color ? "group-hover:border-[var(--wc)]" : "group-hover:border-brand-300"
        )}
      >
        <span
          className={cn(
            "flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-bold ring-1 transition-colors group-hover:text-white",
            color
              ? "bg-[var(--wc-soft)] text-[var(--wc)] ring-[var(--wc-ring)] group-hover:bg-[var(--wc)] group-hover:ring-[var(--wc)]"
              : "bg-brand-soft text-brand-700 ring-brand-100 group-hover:bg-brand group-hover:ring-brand"
          )}
          aria-hidden
        >
          {initials(name)}
        </span>
        <span className="min-w-0 flex-1 truncate font-semibold text-ink">{name}</span>
        <ChevronLeft
          className={cn(
            "h-5 w-5 shrink-0 text-slate-400 transition-all group-hover:-translate-x-0.5",
            color ? "group-hover:text-[var(--wc)]" : "group-hover:text-brand"
          )}
        />
      </Card>
    </Link>
  );
}
