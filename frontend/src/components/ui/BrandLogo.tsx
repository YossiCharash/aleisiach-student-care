import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

export function BrandLogo({
  className,
  animated = true,
}: {
  className?: string;
  animated?: boolean;
}): ReactNode {
  return (
    <span className={cn("brand-logo", animated && "is-animated", className)}>
      <img src="/logo.png" alt="עלי שיח" />
    </span>
  );
}
