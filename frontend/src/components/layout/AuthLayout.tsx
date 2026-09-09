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
    <div className="flex min-h-screen bg-surface">
      <aside className="relative flex w-[42%] max-w-2xl flex-col justify-between overflow-hidden bg-brand p-14 text-white">
        <span
          className="absolute -top-32 -start-28 h-[26rem] w-[26rem] rounded-full bg-brand-400/40"
          aria-hidden
        />
        <span
          className="absolute -bottom-24 -end-20 h-72 w-72 rounded-full bg-brand-700/40"
          aria-hidden
        />

        <span className="relative inline-flex w-fit items-center rounded-2xl bg-white/95 px-4 py-3">
          <img src="/logo.png" alt="עלי שיח" className="h-9 w-auto" />
        </span>

        <div className="relative">
          <h2 className="text-3xl font-extrabold leading-snug text-white">
            מערכת ניהול
            <br />
            הטיפול בתלמיד
          </h2>
          <p className="mt-4 max-w-sm text-[15px] leading-relaxed text-brand-100">
            תוכניות קידום, ישיבות צוות ודוחות תפקודיים — במקום אחד, מאובטח ומסודר.
          </p>
        </div>

        <div className="relative text-xs text-brand-200">עלי שיח · מרכז יום שיקומי</div>
      </aside>

      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <h1 className="text-2xl font-extrabold text-ink">{title}</h1>
          {subtitle && <p className="mt-2 text-sm text-ink-muted">{subtitle}</p>}
          <div className="mt-8">{children}</div>
        </div>
      </div>
    </div>
  );
}
