import { useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { workshopsApi, studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { groupByWorkshop, type WorkshopGroup } from "@/lib/students/groupByWorkshop";
import { studentCountLabel } from "@/lib/utils/hebrew";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { StudentLinkCard } from "@/components/StudentLinkCard";
import { CreateStudentDialog } from "@/pages/students/CreateStudentDialog";

export function StudentsPage(): ReactNode {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const workshopFilter = searchParams.get("workshop");
  const [createOpen, setCreateOpen] = useState(false);
  const studentsQuery = useQuery({
    queryKey: queryKeys.students,
    queryFn: studentsApi.list,
  });
  const workshopsQuery = useQuery({
    queryKey: queryKeys.workshops,
    queryFn: workshopsApi.list,
  });

  const canCreate = user ? permissions.canCreateStudents(user) : false;
  const isLoading = studentsQuery.isLoading || workshopsQuery.isLoading;
  const error = studentsQuery.error ?? workshopsQuery.error;
  const isReady = studentsQuery.data !== undefined && workshopsQuery.data !== undefined;

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">תלמידים</h1>
          <p className="mt-1 text-sm text-ink-muted">
            התלמידים מסודרים לפי סדנאות. לחצו על תלמיד לצפייה בתיק.
          </p>
          {workshopFilter && (
            <Link
              to="/students"
              className="mt-1 inline-block text-sm font-medium text-brand hover:underline"
            >
              הצגת כל הסדנאות
            </Link>
          )}
        </div>
        {canCreate && (
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" />
            תלמיד חדש
          </Button>
        )}
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {!isLoading && !error && isReady && (
        <StudentGroups
          groups={groupByWorkshop(
            workshopFilter
              ? studentsQuery.data.filter(
                  (student) => student.workshop_id === workshopFilter
                )
              : studentsQuery.data,
            workshopsQuery.data
          )}
        />
      )}

      {canCreate && (
        <CreateStudentDialog open={createOpen} onOpenChange={setCreateOpen} />
      )}
    </div>
  );
}

function StudentGroups({ groups }: { groups: WorkshopGroup[] }): ReactNode {
  if (groups.length === 0) {
    return <EmptyState>אין תלמידים להצגה עדיין.</EmptyState>;
  }

  return (
    <div className="space-y-8">
      {groups.map((group) => (
        <section key={group.workshopId}>
          <h2
            className="mb-3 flex items-baseline gap-2 border-b-2 pb-2"
            style={{ borderColor: group.color }}
          >
            <span
              className="inline-block h-3 w-3 shrink-0 self-center rounded-full"
              style={{ backgroundColor: group.color }}
              aria-hidden
            />
            <span className="text-lg font-semibold text-ink">{group.workshopName}</span>
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
