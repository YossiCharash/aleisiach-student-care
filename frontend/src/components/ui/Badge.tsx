import type { HTMLAttributes, ReactNode } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
  {
    variants: {
      tone: {
        neutral: "bg-slate-100 text-ink-muted",
        brand: "bg-brand-50 text-brand-700",
        green: "bg-accent-50 text-accent-700",
        yellow: "bg-amber-50 text-amber-700",
        red: "bg-red-50 text-red-700",
      },
    },
    defaultVariants: { tone: "neutral" },
  }
);

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, tone, ...props }: BadgeProps): ReactNode {
  return <span className={cn(badgeVariants({ tone }), className)} {...props} />;
}
