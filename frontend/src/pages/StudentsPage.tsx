import { useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { workshopsApi, studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { WorkshopResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { groupByWorkshop, type WorkshopGroup } from "@/lib/students/groupByWorkshop";
import { studentCountLabel } from "@/lib/utils/hebrew";
import { cn } from "@/lib/utils/cn";
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

  const visibleStudents = (studentsQuery.data ?? []).filter(
    (student) => workshopFilter === null || student.workshop_id === workshopFilter
  );

  return (
    <div>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-extrabold text-ink">תלמידים</h1>
            {isReady && (
              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-sm font-semibold text-ink-muted">
                {visibleStudents.length}
              </span>
            )}
          </div>
          <p className="mt-2 text-sm text-ink-muted">
            התלמידים מסודרים לפי סדנאות. לחצו על תלמיד לצפייה בתיק.
          </p>
        </div>
        {canCreate && (
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" />
            תלמיד חדש
          </Button>
        )}
      </div>

      {isReady && workshopsQuery.data.length > 0 && (
        <WorkshopFilters workshops={workshopsQuery.data} activeId={workshopFilter} />
      )}

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {!isLoading && !error && isReady && (
        <StudentGroups groups={groupByWorkshop(visibleStudents, workshopsQuery.data)} />
      )}

      {canCreate && (
        <CreateStudentDialog open={createOpen} onOpenChange={setCreateOpen} />
      )}
    </div>
  );
}

function WorkshopFilters({
  workshops,
  activeId,
}: {
  workshops: WorkshopResponse[];
  activeId: string | null;
}): ReactNode {
  return (
    <div className="mb-6 flex flex-wrap items-center gap-2">
      <FilterChip to="/students" label="כל הסדנאות" active={activeId === null} />
      {workshops.map((workshop) => (
        <FilterChip
          key={workshop.id}
          to={`/students?workshop=${workshop.id}`}
          label={workshop.name}
          color={workshop.color}
          active={activeId === workshop.id}
        />
      ))}
    </div>
  );
}

function FilterChip({
  to,
  label,
  active,
  color,
}: {
  to: string;
  label: string;
  active: boolean;
  color?: string;
}): ReactNode {
  return (
    <Link
      to={to}
      aria-current={active ? "true" : undefined}
      className={cn(
        "inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm transition-colors",
        active
          ? "bg-brand font-semibold text-white"
          : "border border-slate-200 bg-white text-ink-muted hover:border-brand-300 hover:text-ink"
      )}
    >
      {color && (
        <span
          className="h-2 w-2 rounded-full"
          style={{ backgroundColor: color }}
          aria-hidden
        />
      )}
      {label}
    </Link>
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
            className="mb-4 flex items-baseline gap-2.5 border-b-2 pb-2.5"
            style={{ borderColor: group.color }}
          >
            <span
              className="inline-block h-2.5 w-2.5 shrink-0 self-center rounded-full"
              style={{ backgroundColor: group.color }}
              aria-hidden
            />
            <span className="text-lg font-bold text-ink">{group.workshopName}</span>
            <span className="text-sm text-ink-muted">
              {studentCountLabel(group.students.length)}
            </span>
          </h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
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
