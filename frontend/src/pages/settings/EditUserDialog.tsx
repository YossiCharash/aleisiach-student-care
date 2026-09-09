import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { UserResponse, UserRole } from "@/lib/api/types";
import { roleLabels } from "@/lib/utils/hebrew";
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

interface Props {
  user: UserResponse;
  isSelf: boolean;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const roles: UserRole[] = ["manager", "instructor", "professional_teacher"];

export function EditUserDialog({ user, isSelf, open, onOpenChange }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState(user.full_name);
  const [email, setEmail] = useState(user.email);
  const [role, setRole] = useState<UserRole>(user.role);

  useEffect(() => {
    if (open) {
      setFullName(user.full_name);
      setEmail(user.email);
      setRole(user.role);
    }
  }, [open, user.full_name, user.email, user.role]);

  const mutation = useMutation({
    mutationFn: () =>
      usersApi.update(user.id, {
        full_name: fullName.trim(),
        email: email.trim(),
        role,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.users });
      onOpenChange(false);
    },
  });

  function handleSubmit(event: FormEvent): void {
    event.preventDefault();
    mutation.mutate();
  }

  const emailChanged = email.trim() !== user.email;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>עריכת משתמש</DialogTitle>
          <DialogDescription>
            שם, דוא״ל ותפקיד. שיוך המדריך לסדנה נעשה בעריכת הסדנה.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          {emailChanged && user.status === "invited" && (
            <Alert tone="info">
              המשתמש טרם אישר את ההזמנה. שינוי הדוא״ל יבטל את הקישור שנשלח וישלח הזמנה
              חדשה לכתובת החדשה.
            </Alert>
          )}
          <div>
            <Label htmlFor="edit-user-name">שם מלא</Label>
            <Input
              id="edit-user-name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="edit-user-email">דוא״ל</Label>
            <Input
              id="edit-user-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="edit-user-role">תפקיד</Label>
            <select
              id="edit-user-role"
              value={role}
              disabled={isSelf}
              onChange={(event) => setRole(event.target.value as UserRole)}
              className="h-10 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm disabled:bg-slate-100"
            >
              {roles.map((value) => (
                <option key={value} value={value}>
                  {roleLabels[value]}
                </option>
              ))}
            </select>
            {isSelf && (
              <p className="mt-1 text-xs text-ink-muted">
                אי אפשר לשנות את התפקיד של החשבון שלך.
              </p>
            )}
          </div>
          <div className="flex justify-start gap-2">
            <Button type="submit" disabled={mutation.isPending || fullName.trim() === ""}>
              {mutation.isPending ? "שומר…" : "שמירה"}
            </Button>
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
              ביטול
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
