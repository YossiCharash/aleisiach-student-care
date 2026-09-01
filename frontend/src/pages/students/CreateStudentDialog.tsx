import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
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

export function CreateStudentDialog({ open, onOpenChange }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState("");
  const [classId, setClassId] = useState("");
  const [nationalId, setNationalId] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      studentsApi.create({
        full_name: fullName,
        class_id: classId,
        national_id: nationalId.trim() || null,
        date_of_birth: dateOfBirth || null,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.students });
      setFullName("");
      setClassId("");
      setNationalId("");
      setDateOfBirth("");
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
          <DialogTitle>תלמיד חדש</DialogTitle>
          <DialogDescription>הוספת תלמיד לכיתה.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          <div>
            <Label htmlFor="student-name">שם מלא</Label>
            <Input
              id="student-name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
              autoFocus
            />
          </div>
          <ClassPicker
            id="student-class"
            value={classId}
            onChange={setClassId}
            required
          />
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="student-national-id">תעודת זהות</Label>
              <Input
                id="student-national-id"
                value={nationalId}
                onChange={(event) => setNationalId(event.target.value)}
                inputMode="numeric"
              />
            </div>
            <div>
              <Label htmlFor="student-dob">תאריך לידה</Label>
              <Input
                id="student-dob"
                type="date"
                value={dateOfBirth}
                onChange={(event) => setDateOfBirth(event.target.value)}
              />
            </div>
          </div>
          <p className="text-sm text-ink-muted">
            שאר הפרטים יושלמו בהמשך בלשונית "פרטי תלמיד".
          </p>
          <div className="flex justify-start gap-2">
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "שומר…" : "הוספה"}
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
