import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/Button";

export function NotFoundPage(): ReactNode {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 text-center">
      <div className="text-5xl font-bold text-brand">404</div>
      <p className="text-ink-muted">העמוד המבוקש לא נמצא.</p>
      <Button asChild>
        <Link to="/">חזרה לעמוד הבית</Link>
      </Button>
    </div>
  );
}
