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
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-6 py-12 bg-[radial-gradient(130%_100%_at_100%_0%,#F6FBEE_0%,#EFF6E2_45%,#E4EFD2_100%)]">
      <span
        className="animate-blob absolute -start-24 -top-24 h-96 w-96 rounded-full bg-accent/30 blur-3xl"
        aria-hidden
      />
      <span
        className="animate-blob absolute -bottom-28 -end-20 h-80 w-80 rounded-full bg-brand/15 blur-3xl [animation-delay:2s]"
        aria-hidden
      />
      <span
        className="absolute inset-y-0 start-0 w-1.5 bg-gradient-to-b from-accent to-brand"
        aria-hidden
      />

      <div className="relative w-full max-w-md animate-fade-up rounded-[22px] border border-white/70 bg-white/75 p-9 text-center shadow-lift backdrop-blur-md">
        <div className="flex justify-center">
          <BrandLogo className="w-52" />
        </div>

        <p className="eyebrow mt-6 block">מפעל עבודה שיקומי</p>
        <h1 className="mt-2 text-[1.75rem] font-semibold tracking-tight text-ink">
          {title}
        </h1>
        {subtitle && <p className="mt-2 text-sm text-ink-muted">{subtitle}</p>}

        <div className="mt-8 text-start">{children}</div>
      </div>
    </div>
  );
}
