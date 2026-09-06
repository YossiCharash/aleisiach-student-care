import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { classesApi, meetingsApi, studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  ClassResponse,
  MeetingOverviewItem,
  StudentResponse,
} from "@/lib/api/types";
import { groupByClass, type ClassGroup } from "@/lib/students/groupByClass";
import { formatMonthYear, studentCountLabel } from "@/lib/utils/hebrew";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { StudentLinkCard } from "@/components/StudentLinkCard";

export function MeetingsOverviewPage(): ReactNode {
  const overviewQuery = useQuery({
    queryKey: queryKeys.meetingsOverview,
    queryFn: meetingsApi.overview,
  });
  const studentsQuery = useQuery({
    queryKey: queryKeys.students,
    queryFn: studentsApi.list,
  });
  const classesQuery = useQuery({
    queryKey: queryKeys.classes,
    queryFn: classesApi.list,
  });

  const isLoading =
    overviewQuery.isLoading || studentsQuery.isLoading || classesQuery.isLoading;
  const error = overviewQuery.error ?? studentsQuery.error ?? classesQuery.error;
  const isReady =
    overviewQuery.data !== undefined &&
    studentsQuery.data !== undefined &&
    classesQuery.data !== undefined;

  const now = new Date();

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-ink">ישיבות צוות</h1>
        <p className="mt-1 text-sm text-ink-muted">
          תלמידים שטרם נערכה להם ישיבה ב
          {formatMonthYear(now.getFullYear(), now.getMonth() + 1)}, מסודרים לפי כיתות.
          לחצו על תלמיד כדי לפתוח ישיבה חודשית חדשה.
        </p>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {!isLoading && !error && isReady && (
        <PendingByClass
          overview={overviewQuery.data}
          students={studentsQuery.data}
          classes={classesQuery.data}
        />
      )}
    </div>
  );
}

function PendingByClass({
  overview,
  students,
  classes,
}: {
  overview: MeetingOverviewItem[];
  students: StudentResponse[];
  classes: ClassResponse[];
}): ReactNode {
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;

  const metThisMonth = new Set(
    overview
      .filter((item) => item.year === currentYear && item.month === currentMonth)
      .map((item) => item.student_id)
  );
  const pending = students.filter(
    (student) => !student.is_archived && !metThisMonth.has(student.id)
  );
  const groups = groupByClass(pending, classes);

  if (groups.length === 0) {
    return <EmptyState>כל התלמידים כבר נערכה להם ישיבה החודש.</EmptyState>;
  }

  return (
    <div className="space-y-8">
      {groups.map((group) => (
        <ClassSection key={group.classId} group={group} />
      ))}
    </div>
  );
}

function ClassSection({ group }: { group: ClassGroup }): ReactNode {
  return (
    <section>
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
            to={`/students/${student.id}?tab=meetings&new=1`}
          />
        ))}
      </div>
    </section>
  );
}
