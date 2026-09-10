import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>): ReactNode {
  return (
    <div
      className={cn(
        "rounded-card border border-slate-200/70 bg-surface-raised shadow-card",
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>): ReactNode {
  return (
    <div className={cn("border-b border-slate-200/70 px-6 py-5", className)} {...props} />
  );
}

export function CardTitle({
  className,
  ...props
}: HTMLAttributes<HTMLHeadingElement>): ReactNode {
  return (
    <h3
      className={cn("text-lg font-semibold tracking-tight text-ink", className)}
      {...props}
    />
  );
}

export function CardContent({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>): ReactNode {
  return <div className={cn("px-6 py-5", className)} {...props} />;
}
