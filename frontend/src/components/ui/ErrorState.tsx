import type { ReactNode } from "react";
import { ApiError } from "@/lib/api/client";
import { Alert } from "@/components/ui/Alert";

export function errorMessage(error: unknown, fallback = "אירעה שגיאה. נסו שוב."): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error && error.message) {
    return error.message;
  }
  return fallback;
}

export function ErrorState({ error }: { error: unknown }): ReactNode {
  return <Alert tone="error">{errorMessage(error)}</Alert>;
}

export function EmptyState({ children }: { children: ReactNode }): ReactNode {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 py-10 text-center text-ink-muted">
      {children}
    </div>
  );
}
