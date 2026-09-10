import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils/cn";

const buttonVariants = cva(
  "inline-flex select-none items-center justify-center gap-2 rounded-control text-sm font-semibold transition-all duration-150 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2 focus-visible:ring-offset-surface active:translate-y-px disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none",
  {
    variants: {
      variant: {
        primary:
          "bg-brand bg-gradient-to-b from-brand-400 to-brand text-white shadow-brand-sm hover:-translate-y-px hover:shadow-brand",
        secondary:
          "bg-accent text-white shadow-soft hover:-translate-y-px hover:bg-accent-500",
        outline:
          "border border-slate-300 bg-white/80 text-ink shadow-soft hover:border-brand-300 hover:bg-brand-50/60 hover:text-brand-700",
        ghost: "text-ink-muted hover:bg-slate-100 hover:text-ink",
        danger:
          "bg-rating-red text-white shadow-soft hover:-translate-y-px hover:bg-red-700",
      },
      size: {
        sm: "h-8 px-3",
        md: "h-10 px-4",
        lg: "h-11 px-6 text-base",
        icon: "h-9 w-9",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Component = asChild ? Slot : "button";
    return (
      <Component
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { buttonVariants };
