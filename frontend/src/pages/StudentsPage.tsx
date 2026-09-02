import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, Plus } from "lucide-react";
import { classesApi, studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { StudentResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { groupByClass, type ClassGroup } from "@/lib/students/groupByClass";
import { studentCountLabel } from "@/lib/utils/hebrew";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { CreateStudentDialog } from "@/pages/students/CreateStudentDialog";

export function StudentsPage(): ReactNode {
  const { user } = useAuth();
  const [createOpen, setCreateOpen] = useState(false);
  const studentsQuery = useQuery({
    queryKey: queryKeys.students,
    queryFn: studentsApi.list,
  });
  const classesQuery = useQuery({
    queryKey: queryKeys.classes,
    queryFn: classesApi.list,
  });

  const canCreate = user ? permissions.canCreateStudents(user) : false;

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
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" />
            תלמיד חדש
          </Button>
        )}
      </div>

      {studentsQuery.isLoading && <LoadingState />}
      {studentsQuery.isError && <ErrorState error={studentsQuery.error} />}
      {studentsQuery.data && (
        <StudentGroups
          groups={groupByClass(studentsQuery.data, classesQuery.data ?? [])}
        />
      )}

      {canCreate && (
        <CreateStudentDialog open={createOpen} onOpenChange={setCreateOpen} />
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
              <StudentCard key={student.id} student={student} />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

function StudentCard({ student }: { student: StudentResponse }): ReactNode {
  return (
    <Link to={`/students/${student.id}`}>
      <Card className="flex items-center justify-between px-5 py-4 transition-colors hover:border-brand-300 hover:bg-brand-50/40">
        <span className="font-medium text-ink">{student.full_name}</span>
        <ChevronLeft className="h-5 w-5 text-slate-400" />
      </Card>
    </Link>
  );
}
