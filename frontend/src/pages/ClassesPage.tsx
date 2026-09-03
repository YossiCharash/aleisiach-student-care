import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus, Settings2 } from "lucide-react";
import { classesApi, studentsApi, usersApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ClassResponse, StudentResponse, UserResponse } from "@/lib/api/types";
import { studentCountLabel } from "@/lib/utils/hebrew";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { CreateClassDialog } from "@/pages/classes/CreateClassDialog";
import { EditClassDialog } from "@/pages/classes/EditClassDialog";

export function ClassesPage(): ReactNode {
  const [createOpen, setCreateOpen] = useState(false);
  const [editing, setEditing] = useState<ClassResponse | null>(null);

  const classesQuery = useQuery({ queryKey: queryKeys.classes, queryFn: classesApi.list });
  const studentsQuery = useQuery({ queryKey: queryKeys.students, queryFn: studentsApi.list });
  const usersQuery = useQuery({ queryKey: queryKeys.users, queryFn: usersApi.list });

  const isLoading =
    classesQuery.isLoading || studentsQuery.isLoading || usersQuery.isLoading;
  const error = classesQuery.error ?? studentsQuery.error ?? usersQuery.error;
  const isReady =
    classesQuery.data !== undefined &&
    studentsQuery.data !== undefined &&
    usersQuery.data !== undefined;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">כיתות</h1>
          <p className="mt-1 text-sm text-ink-muted">
            ניהול הכיתות — שם, מדריך ושיוך תלמידים. לחצו על גלגל השיניים לעריכה.
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" />
          כיתה חדשה
        </Button>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {!isLoading && !error && isReady && (
        <ClassCards
          classes={classesQuery.data}
          students={studentsQuery.data}
          users={usersQuery.data}
          onEdit={setEditing}
        />
      )}

      <CreateClassDialog open={createOpen} onOpenChange={setCreateOpen} />
      {editing && (
        <EditClassDialog
          classItem={editing}
          open={editing !== null}
          onOpenChange={(open) => {
            if (!open) {
              setEditing(null);
            }
          }}
        />
      )}
    </div>
  );
}

function ClassCards({
  classes,
  students,
  users,
  onEdit,
}: {
  classes: ClassResponse[];
  students: StudentResponse[];
  users: UserResponse[];
  onEdit: (classItem: ClassResponse) => void;
}): ReactNode {
  if (classes.length === 0) {
    return <EmptyState>אין כיתות עדיין. הוסיפו כיתה חדשה כדי להתחיל.</EmptyState>;
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {classes.map((classItem) => {
        const count = students.filter(
          (student) => !student.is_archived && student.class_id === classItem.id
        ).length;
        const instructor = users.find(
          (user) => user.role === "instructor" && user.class_id === classItem.id
        );
        return (
          <Card key={classItem.id} className="flex items-start justify-between p-5">
            <div>
              <div className="text-lg font-semibold text-ink">{classItem.name}</div>
              <div className="mt-1 text-sm text-ink-muted">
                {instructor ? `מדריך: ${instructor.full_name}` : "ללא מדריך"}
              </div>
              <div className="mt-0.5 text-sm text-ink-muted">
                {studentCountLabel(count)}
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              title="עריכת כיתה"
              onClick={() => onEdit(classItem)}
            >
              <Settings2 className="h-5 w-5" />
            </Button>
          </Card>
        );
      })}
    </div>
  );
}
