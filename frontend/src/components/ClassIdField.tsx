import type { ReactNode } from "react";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";

interface Props {
  id: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
}

export function ClassIdField({ id, value, onChange, required = false }: Props): ReactNode {
  return (
    <div>
      <Label htmlFor={id}>מזהה כיתה</Label>
      <Input
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="UUID של הכיתה"
        required={required}
      />
      <p className="mt-1 text-xs text-ink-muted">זמני — עד להוספת ניהול כיתות בצד השרת.</p>
    </div>
  );
}
