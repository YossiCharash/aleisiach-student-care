import { Loader2 } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

export function Spinner({ className }: { className?: string }): ReactNode {
  return <Loader2 className={cn("h-5 w-5 animate-spin text-brand", className)} aria-hidden />;
}

export function LoadingState({ label = "טוען…" }: { label?: string }): ReactNode {
  return (
    <div className="flex items-center justify-center gap-2 py-10 text-ink-muted" role="status">
      <Spinner />
      <span>{label}</span>
    </div>
  );
}
