import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { classesApi, studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { groupByClass, type ClassGroup } from "@/lib/students/groupByClass";
import { studentCountLabel } from "@/lib/utils/hebrew";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { StudentLinkCard } from "@/components/StudentLinkCard";
import { CreateStudentDialog } from "@/pages/students/CreateStudentDialog";
import { CreateClassDialog } from "@/pages/classes/CreateClassDialog";

export function StudentsPage(): ReactNode {
  const { user } = useAuth();
  const [createOpen, setCreateOpen] = useState(false);
  const [createClassOpen, setCreateClassOpen] = useState(false);
  const studentsQuery = useQuery({
    queryKey: queryKeys.students,
    queryFn: studentsApi.list,
  });
  const classesQuery = useQuery({
    queryKey: queryKeys.classes,
    queryFn: classesApi.list,
  });

  const canCreate = user ? permissions.canCreateStudents(user) : false;
  const isLoading = studentsQuery.isLoading || classesQuery.isLoading;
  const error = studentsQuery.error ?? classesQuery.error;
  const isReady = studentsQuery.data !== undefined && classesQuery.data !== undefined;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">תלמידים</h1>
          <p className="mt-1 text-sm text-ink-muted">
            התלמידים מסודרים לפי כיתות. לחצו על תלמיד לצפייה בתיק.
          </p>
        </div>
        {canCreate && (
          <div className="flex gap-2">
            <Button onClick={() => setCreateOpen(true)}>
              <Plus className="h-4 w-4" />
              תלמיד חדש
            </Button>
            <Button variant="outline" onClick={() => setCreateClassOpen(true)}>
              <Plus className="h-4 w-4" />
              כיתה חדשה
            </Button>
          </div>
        )}
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {!isLoading && !error && isReady && (
        <StudentGroups groups={groupByClass(studentsQuery.data, classesQuery.data)} />
      )}

      {canCreate && (
        <>
          <CreateStudentDialog open={createOpen} onOpenChange={setCreateOpen} />
          <CreateClassDialog open={createClassOpen} onOpenChange={setCreateClassOpen} />
        </>
      )}
    </div>
  );
}

function StudentGroups({ groups }: { groups: ClassGroup[] }): ReactNode {
  if (groups.length === 0) {
    return <EmptyState>אין תלמידים להצגה עדיין.</EmptyState>;
  }

  return (
    <div className="space-y-8">
      {groups.map((group) => (
        <section key={group.classId}>
          <h2 className="mb-3 flex items-baseline gap-2 border-b border-slate-200 pb-2">
            <span className="text-lg font-semibold text-ink">{group.className}</span>
            <span className="text-sm text-ink-muted">
              {studentCountLabel(group.students.length)}
            </span>
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {group.students.map((student) => (
              <StudentLinkCard
                key={student.id}
                id={student.id}
                name={student.full_name}
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
