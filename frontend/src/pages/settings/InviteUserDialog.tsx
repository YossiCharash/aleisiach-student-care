import { useState, type FormEvent, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { authApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { InvitableRole } from "@/lib/api/types";
import { invitableRoleLabels } from "@/lib/utils/hebrew";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import { ClassPicker } from "@/components/ClassPicker";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface InviteRow {
  key: string;
  fullName: string;
  email: string;
  role: InvitableRole;
  classId: string;
}

interface RowFailure {
  key: string;
  email: string;
  message: string;
}

let rowIdCounter = 0;

function newRow(): InviteRow {
  rowIdCounter += 1;
  return {
    key: `invite-row-${rowIdCounter}`,
    fullName: "",
    email: "",
    role: "instructor",
    classId: "",
  };
}

export function InviteUserDialog({ open, onOpenChange }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [rows, setRows] = useState<InviteRow[]>([newRow()]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [failures, setFailures] = useState<RowFailure[]>([]);

  function reset(): void {
    setRows([newRow()]);
    setFailures([]);
  }

  function updateRow(key: string, patch: Partial<InviteRow>): void {
    setRows((current) =>
      current.map((row) => (row.key === key ? { ...row, ...patch } : row))
    );
  }

  function addRow(): void {
    setRows((current) => [...current, newRow()]);
  }

  function removeRow(key: string): void {
    setRows((current) =>
      current.length === 1 ? current : current.filter((row) => row.key !== key)
    );
  }

  async function handleSubmit(event: FormEvent): Promise<void> {
    event.preventDefault();
    setIsSubmitting(true);
    setFailures([]);
    const collected: RowFailure[] = [];
    for (const row of rows) {
      try {
        await authApi.createInvitation({
          full_name: row.fullName,
          email: row.email,
          role: row.role,
          class_id: row.role === "instructor" ? row.classId || null : null,
        });
      } catch (error) {
        collected.push({ key: row.key, email: row.email, message: errorMessage(error) });
      }
    }
    setIsSubmitting(false);
    void queryClient.invalidateQueries({ queryKey: queryKeys.users });

    if (collected.length === 0) {
      reset();
      onOpenChange(false);
      return;
    }
    setFailures(collected);
    setRows((current) =>
      current.filter((row) => collected.some((failure) => failure.key === row.key))
    );
  }

  function handleOpenChange(next: boolean): void {
    if (!next) {
      reset();
    }
    onOpenChange(next);
  }

  const submitLabel = rows.length > 1 ? "שליחת הזמנות" : "שליחת הזמנה";

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>הזמנת משתמשים</DialogTitle>
          <DialogDescription>
            ניתן להוסיף מספר משתמשים בבת אחת. יישלח קישור הזמנה לכל כתובת דוא״ל.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {failures.length > 0 && (
            <Alert tone="error">
              חלק מההזמנות נכשלו — נותרו למטה לתיקון:
              <ul className="mt-1 list-inside list-disc">
                {failures.map((failure) => (
                  <li key={failure.email}>
                    {failure.email || "(ללא דוא״ל)"} — {failure.message}
                  </li>
                ))}
              </ul>
            </Alert>
          )}

          <div className="max-h-[55vh] space-y-3 overflow-y-auto">
            {rows.map((row, index) => (
              <div
                key={row.key}
                className="rounded-lg border border-slate-200 bg-slate-50 p-3"
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium text-ink-muted">
                    משתמש {index + 1}
                  </span>
                  {rows.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeRow(row.key)}
                      className="rounded-md p-1 text-slate-400 hover:bg-slate-200 hover:text-rating-red"
                      aria-label="הסרת משתמש"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor={`invite-name-${row.key}`}>שם מלא</Label>
                    <Input
                      id={`invite-name-${row.key}`}
                      value={row.fullName}
                      onChange={(event) =>
                        updateRow(row.key, { fullName: event.target.value })
                      }
                      required
                      autoFocus={index === 0}
                    />
                  </div>
                  <div>
                    <Label htmlFor={`invite-email-${row.key}`}>דוא״ל</Label>
                    <Input
                      id={`invite-email-${row.key}`}
                      type="email"
                      value={row.email}
                      onChange={(event) =>
                        updateRow(row.key, { email: event.target.value })
                      }
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor={`invite-role-${row.key}`}>תפקיד</Label>
                    <select
                      id={`invite-role-${row.key}`}
                      value={row.role}
                      onChange={(event) =>
                        updateRow(row.key, { role: event.target.value as InvitableRole })
                      }
                      className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm"
                    >
                      {(Object.keys(invitableRoleLabels) as InvitableRole[]).map(
                        (value) => (
                          <option key={value} value={value}>
                            {invitableRoleLabels[value]}
                          </option>
                        )
                      )}
                    </select>
                  </div>
                  {row.role === "instructor" && (
                    <ClassPicker
                      id={`invite-class-${row.key}`}
                      value={row.classId}
                      onChange={(value) => updateRow(row.key, { classId: value })}
                      required
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

          <Button type="button" variant="ghost" onClick={addRow}>
            <Plus className="h-4 w-4" />
            הוספת משתמש נוסף
          </Button>

          <div className="flex justify-start gap-2 border-t border-slate-100 pt-4">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "שולח…" : submitLabel}
            </Button>
            <Button type="button" variant="ghost" onClick={() => handleOpenChange(false)}>
              ביטול
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
