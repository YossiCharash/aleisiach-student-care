import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { StudentResponse } from "@/lib/api/types";
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
  student: StudentResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EditStudentDialog({ student, open, onOpenChange }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState(student.full_name);
  const [classId, setClassId] = useState(student.class_id);

  useEffect(() => {
    if (open) {
      setFullName(student.full_name);
      setClassId(student.class_id);
    }
  }, [open, student.full_name, student.class_id]);

  const mutation = useMutation({
    mutationFn: () =>
      studentsApi.update(student.id, { full_name: fullName.trim(), class_id: classId }),
    onSuccess: (updated) => {
      queryClient.setQueryData(queryKeys.student(student.id), updated);
      void queryClient.invalidateQueries({ queryKey: queryKeys.students });
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
          <DialogTitle>עריכת פרטי תלמיד</DialogTitle>
          <DialogDescription>
            שם התלמיד והכיתה שאליה הוא משויך. שאר הפרטים נערכים בלשונית "פרטי תלמיד".
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          <div>
            <Label htmlFor="edit-student-name">שם מלא</Label>
            <Input
              id="edit-student-name"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
              autoFocus
            />
          </div>
          <ClassPicker
            id="edit-student-class"
            value={classId}
            onChange={setClassId}
            required
          />
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
