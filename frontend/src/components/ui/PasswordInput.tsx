import { forwardRef, useState, type ReactNode } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Input, type InputProps } from "@/components/ui/Input";
import { cn } from "@/lib/utils/cn";

export type PasswordInputProps = Omit<InputProps, "type">;

export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ className, ...props }, ref): ReactNode => {
    const [visible, setVisible] = useState(false);
    return (
      <div className="relative">
        <Input
          ref={ref}
          type={visible ? "text" : "password"}
          className={cn("pe-10", className)}
          {...props}
        />
        <button
          type="button"
          onClick={() => setVisible((current) => !current)}
          className="absolute inset-y-0 end-0 flex items-center pe-3 text-slate-500 hover:text-ink focus-visible:outline-none focus-visible:text-ink"
          aria-label={visible ? "הסתרת הסיסמה" : "הצגת הסיסמה"}
          aria-pressed={visible}
          tabIndex={-1}
        >
          {visible ? (
            <EyeOff className="h-4 w-4" aria-hidden />
          ) : (
            <Eye className="h-4 w-4" aria-hidden />
          )}
        </button>
      </div>
    );
  }
);
PasswordInput.displayName = "PasswordInput";
