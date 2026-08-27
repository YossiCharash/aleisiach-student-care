import type { ReactNode } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils/cn";

const alertVariants = cva("rounded-lg border px-4 py-3 text-sm", {
  variants: {
    tone: {
      error: "border-red-200 bg-red-50 text-red-700",
      success: "border-accent-200 bg-accent-50 text-accent-700",
      info: "border-slate-200 bg-slate-50 text-ink-muted",
    },
  },
  defaultVariants: { tone: "info" },
});

interface AlertProps extends VariantProps<typeof alertVariants> {
  children: ReactNode;
  className?: string;
}

export function Alert({ tone, children, className }: AlertProps): ReactNode {
  return (
    <div role="alert" className={cn(alertVariants({ tone }), className)}>
      {children}
    </div>
  );
}
