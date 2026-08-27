import type { ReactNode } from "react";

export function AuthLayout({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}): ReactNode {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-brand-50 to-slate-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <div className="text-3xl font-bold text-brand">עלי שיח</div>
          <div className="mt-1 text-sm text-ink-muted">מערכת ניהול תלמידים</div>
        </div>
        <div className="rounded-card border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-xl font-semibold text-ink">{title}</h1>
          {subtitle && <p className="mt-1 text-sm text-ink-muted">{subtitle}</p>}
          <div className="mt-6">{children}</div>
        </div>
      </div>
    </div>
  );
}
