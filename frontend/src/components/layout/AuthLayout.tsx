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
    <div className="flex min-h-screen">
      <aside className="relative hidden w-[44%] max-w-2xl flex-col justify-between overflow-hidden bg-brand p-14 text-white md:flex">
        <span
          className="absolute -start-40 -top-40 h-[34rem] w-[34rem] rounded-full border border-white/10"
          aria-hidden
        />
        <span
          className="absolute -start-24 -top-24 h-[26rem] w-[26rem] rounded-full border border-white/10"
          aria-hidden
        />
        <span
          className="absolute -bottom-32 -end-28 h-[30rem] w-[30rem] rounded-full bg-accent/25 blur-3xl"
          aria-hidden
        />
        <span
          className="absolute inset-0 bg-[radial-gradient(120%_80%_at_0%_0%,rgba(133,196,65,0.30),transparent_55%)]"
          aria-hidden
        />

        <span className="relative inline-flex w-fit items-center rounded-2xl bg-white px-4 py-3 shadow-lift">
          <img src="/logo.png" alt="עלי שיח" className="h-10 w-auto" />
        </span>

        <div className="relative">
          <p className="eyebrow text-accent-200">מרכז יום שיקומי</p>
          <h2 className="mt-4 text-4xl font-light leading-[1.15] tracking-tight text-white">
            מערכת ניהול
            <br />
            <span className="font-semibold">הטיפול בתלמיד</span>
          </h2>
          <p className="mt-5 max-w-sm text-[15px] leading-relaxed text-brand-100">
            תוכניות קידום, ישיבות צוות ודוחות תפקודיים — במקום אחד, מאובטח ומסודר.
          </p>
        </div>

        <div className="relative flex items-center gap-2.5 text-xs text-brand-200">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-accent" aria-hidden />
          עלי שיח · ליווי וקידום תלמידים
        </div>
      </aside>

      <div className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm animate-fade-up">
          <p className="eyebrow">עלי שיח</p>
          <h1 className="mt-3 text-[1.75rem] font-semibold tracking-tight text-ink">
            {title}
          </h1>
          {subtitle && <p className="mt-2 text-sm text-ink-muted">{subtitle}</p>}
          <div className="mt-8">{children}</div>
        </div>
      </div>
    </div>
  );
}
