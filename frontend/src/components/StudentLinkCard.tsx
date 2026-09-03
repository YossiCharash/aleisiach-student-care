import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { Card } from "@/components/ui/Card";

export function StudentLinkCard({ id, name }: { id: string; name: string }): ReactNode {
  return (
    <Link to={`/students/${id}`}>
      <Card className="flex items-center justify-between px-5 py-4 transition-colors hover:border-brand-300 hover:bg-brand-50/40">
        <span className="font-medium text-ink">{name}</span>
        <ChevronLeft className="h-5 w-5 text-slate-400" />
      </Card>
    </Link>
  );
}
