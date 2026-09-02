import type { ReactNode } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  institutionName: string;
  isPending: boolean;
  onConfirm: () => void;
}

export function ConfirmDeactivationDialog({
  open,
  onOpenChange,
  institutionName,
  isPending,
  onConfirm,
}: Props): ReactNode {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>השבתת המוסד «{institutionName}»</DialogTitle>
          <DialogDescription>
            כל משתמשי המוסד לא יוכלו להתחבר, והנתונים יישמרו במלואם. אפשר להפעיל את המוסד
            מחדש בכל עת.
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-start gap-2 border-t border-slate-100 pt-4">
          <Button onClick={onConfirm} disabled={isPending}>
            {isPending ? "משבית…" : "השבתה"}
          </Button>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            ביטול
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
