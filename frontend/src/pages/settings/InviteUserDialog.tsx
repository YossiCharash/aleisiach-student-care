import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { UserRole } from "@/lib/api/types";
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
import { ClassPicker } from "@/components/ClassPicker";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function InviteUserDialog({ open, onOpenChange }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<UserRole>("instructor");
  const [classId, setClassId] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      authApi.createInvitation({
        full_name: fullName,
        email,
        role,
        class_id: role === "instructor" ? classId || null : null,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.users });
      setFullName("");
      setEmail("");
      setRole("instructor");
      setClassId("");
      onOpenChange(false);
    },
  });

  function handleSubmit(event: FormEvent): void {
    event.preventDefault();
    mutation.mutate();
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>הזמנת משתמש</DialogTitle>
          <DialogDescription>ישלח קישור הזמנה לכתובת הדוא״ל.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          <div>
            <Label htmlFor="invite-name">שם מלא</Label>
            <Input
              id="invite-name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="invite-email">דוא״ל</Label>
            <Input
              id="invite-email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div>
            <Label htmlFor="invite-role">תפקיד</Label>
            <select
              id="invite-role"
              value={role}
              onChange={(event) => setRole(event.target.value as UserRole)}
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm"
            >
              {(Object.keys(roleLabels) as UserRole[]).map((value) => (
                <option key={value} value={value}>
                  {roleLabels[value]}
                </option>
              ))}
            </select>
          </div>
          {role === "instructor" && (
            <ClassPicker
              id="invite-class"
              value={classId}
              onChange={setClassId}
              required
            />
          )}
          <div className="flex justify-start gap-2">
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "שולח…" : "שליחת הזמנה"}
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
