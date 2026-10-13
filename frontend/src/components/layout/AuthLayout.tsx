import type { ReactNode } from "react";
import { BrandLogo } from "@/components/ui/BrandLogo";

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
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-12 bg-[linear-gradient(135deg,#356E1A_0%,#3F8420_45%,#4E9A28_100%)]">
      <span
        className="animate-blob absolute -start-28 -top-32 h-[28rem] w-[28rem] rounded-full bg-accent/55 blur-[38px]"
        aria-hidden
      />
      <span
        className="animate-blob absolute -bottom-36 -end-28 h-96 w-96 rounded-full bg-[#2C5E14]/60 blur-[38px] [animation-delay:2.5s]"
        aria-hidden
      />
      <span
        className="animate-blob absolute start-[30%] top-[38%] h-80 w-80 rounded-full bg-white/15 blur-[38px] [animation-delay:1.2s]"
        aria-hidden
      />

      <span className="eyebrow absolute start-8 top-7 text-white/90" aria-hidden>
        עלי שיח
      </span>

      <div className="relative w-full max-w-sm animate-fade-up rounded-[22px] bg-white p-9 text-center shadow-[0_30px_70px_-30px_rgba(0,0,0,0.5)]">
        <div className="flex justify-center">
          <BrandLogo className="w-48" />
        </div>

        <h1 className="mt-6 text-[1.75rem] font-semibold tracking-tight text-ink">
          {title}
        </h1>
        {subtitle && <p className="mt-2 text-sm text-ink-muted">{subtitle}</p>}

        <div className="mt-8 text-start">{children}</div>
      </div>
    </div>
  );
}
