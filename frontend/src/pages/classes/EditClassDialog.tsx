import { useEffect, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { classesApi, studentsApi, usersApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ClassResponse, StudentResponse, UserResponse } from "@/lib/api/types";
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
import { EmptyState, errorMessage } from "@/components/ui/ErrorState";

interface Props {
  classItem: ClassResponse;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const selectClass =
  "h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm disabled:bg-slate-100";

export function EditClassDialog({ classItem, open, onOpenChange }: Props): ReactNode {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>עריכת כיתה</DialogTitle>
          <DialogDescription>שם הכיתה, מדריך הכיתה ושיוך התלמידים.</DialogDescription>
        </DialogHeader>
        {open && (
          <EditClassForm classItem={classItem} onDone={() => onOpenChange(false)} />
        )}
      </DialogContent>
    </Dialog>
  );
}

function EditClassForm({
  classItem,
  onDone,
}: {
  classItem: ClassResponse;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [name, setName] = useState(classItem.name);
  const [addStudentId, setAddStudentId] = useState("");

  useEffect(() => setName(classItem.name), [classItem.id, classItem.name]);

  const classesQuery = useQuery({
    queryKey: queryKeys.classes,
    queryFn: classesApi.list,
  });
  const studentsQuery = useQuery({
    queryKey: queryKeys.students,
    queryFn: studentsApi.list,
  });
  const usersQuery = useQuery({ queryKey: queryKeys.users, queryFn: usersApi.list });

  function invalidate(): void {
    void queryClient.invalidateQueries({ queryKey: queryKeys.classes });
    void queryClient.invalidateQueries({ queryKey: queryKeys.students });
    void queryClient.invalidateQueries({ queryKey: queryKeys.users });
  }

  const rename = useMutation({
    mutationFn: () => classesApi.rename(classItem.id, name.trim()),
    onSuccess: invalidate,
  });

  const moveStudent = useMutation({
    mutationFn: ({ student, classId }: { student: StudentResponse; classId: string }) =>
      studentsApi.update(student.id, { full_name: student.full_name, class_id: classId }),
    onSuccess: invalidate,
  });

  const setInstructor = useMutation({
    mutationFn: async (nextInstructorId: string) => {
      const current = (usersQuery.data ?? []).filter(
        (candidate) =>
          candidate.role === "instructor" && candidate.class_id === classItem.id
      );
      for (const instructor of current) {
        if (instructor.id !== nextInstructorId) {
          await assignInstructorClass(instructor, null);
        }
      }
      if (nextInstructorId !== "") {
        const next = (usersQuery.data ?? []).find((item) => item.id === nextInstructorId);
        if (next) {
          await assignInstructorClass(next, classItem.id);
        }
      }
    },
    onSuccess: invalidate,
  });

  const error =
    classesQuery.error ?? studentsQuery.error ?? usersQuery.error ?? rename.error;
  const mutationError = moveStudent.error ?? setInstructor.error;

  const activeStudents = (studentsQuery.data ?? []).filter(
    (student) => !student.is_archived
  );
  const members = activeStudents.filter((student) => student.class_id === classItem.id);
  const outsiders = activeStudents.filter((student) => student.class_id !== classItem.id);
  const otherClasses = (classesQuery.data ?? []).filter(
    (item) => item.id !== classItem.id
  );
  const instructors = (usersQuery.data ?? []).filter(
    (user) => user.role === "instructor"
  );
  const currentInstructorId =
    instructors.find((user) => user.class_id === classItem.id)?.id ?? "";

  return (
    <div className="space-y-6">
      {error && <Alert tone="error">{errorMessage(error)}</Alert>}
      {mutationError && <Alert tone="error">{errorMessage(mutationError)}</Alert>}

      <div>
        <Label htmlFor="edit-class-name">שם הכיתה</Label>
        <div className="flex gap-2">
          <Input
            id="edit-class-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
          <Button
            type="button"
            variant="outline"
            disabled={
              rename.isPending || name.trim() === "" || name.trim() === classItem.name
            }
            onClick={() => rename.mutate()}
          >
            שמירת שם
          </Button>
        </div>
      </div>

      <div>
        <Label htmlFor="edit-class-instructor">מדריך הכיתה</Label>
        <select
          id="edit-class-instructor"
          className={selectClass}
          value={currentInstructorId}
          disabled={setInstructor.isPending}
          onChange={(event) => setInstructor.mutate(event.target.value)}
        >
          <option value="">— ללא מדריך —</option>
          {instructors.map((instructor) => (
            <option key={instructor.id} value={instructor.id}>
              {instructor.full_name}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <Label>תלמידי הכיתה</Label>
        {members.length === 0 ? (
          <EmptyState>אין תלמידים בכיתה זו.</EmptyState>
        ) : (
          <ul className="space-y-2">
            {members.map((student) => (
              <li
                key={student.id}
                className="flex items-center justify-between gap-3 rounded-lg border border-slate-100 px-3 py-2"
              >
                <span className="text-sm font-medium text-ink">{student.full_name}</span>
                <select
                  className="h-9 rounded-lg border border-slate-300 bg-white px-2 text-sm disabled:bg-slate-100"
                  value=""
                  disabled={moveStudent.isPending || otherClasses.length === 0}
                  onChange={(event) =>
                    moveStudent.mutate({ student, classId: event.target.value })
                  }
                >
                  <option value="" disabled>
                    העברה לכיתה…
                  </option>
                  {otherClasses.map((target) => (
                    <option key={target.id} value={target.id}>
                      {target.name}
                    </option>
                  ))}
                </select>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <Label htmlFor="edit-class-add-student">הוספת תלמיד לכיתה</Label>
        <select
          id="edit-class-add-student"
          className={selectClass}
          value={addStudentId}
          disabled={moveStudent.isPending || outsiders.length === 0}
          onChange={(event) => {
            const student = outsiders.find((item) => item.id === event.target.value);
            if (student) {
              moveStudent.mutate({ student, classId: classItem.id });
            }
            setAddStudentId("");
          }}
        >
          <option value="">בחירת תלמיד להוספה…</option>
          {outsiders.map((student) => (
            <option key={student.id} value={student.id}>
              {student.full_name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex justify-start">
        <Button type="button" variant="ghost" onClick={onDone}>
          סגירה
        </Button>
      </div>
    </div>
  );
}

function assignInstructorClass(
  instructor: UserResponse,
  classId: string | null
): Promise<UserResponse> {
  return usersApi.update(instructor.id, {
    full_name: instructor.full_name,
    email: instructor.email,
    role: instructor.role,
    class_id: classId,
  });
}
