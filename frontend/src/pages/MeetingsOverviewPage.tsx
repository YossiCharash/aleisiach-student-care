import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { meetingsApi, studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { MeetingOverviewItem, StudentResponse } from "@/lib/api/types";
import { formatMonthYear } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { StudentLinkCard } from "@/components/StudentLinkCard";

interface MonthGroup {
  key: number;
  year: number;
  month: number;
  met: MeetingOverviewItem[];
}

export function MeetingsOverviewPage(): ReactNode {
  const overviewQuery = useQuery({
    queryKey: queryKeys.meetingsOverview,
    queryFn: meetingsApi.overview,
  });
  const studentsQuery = useQuery({
    queryKey: queryKeys.students,
    queryFn: studentsApi.list,
  });

  const isLoading = overviewQuery.isLoading || studentsQuery.isLoading;
  const error = overviewQuery.error ?? studentsQuery.error;
  const isReady = overviewQuery.data !== undefined && studentsQuery.data !== undefined;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-ink">ישיבות צוות</h1>
        <p className="mt-1 text-sm text-ink-muted">
          הישיבות מסודרות לפי חודשים. בחודש הנוכחי מוצג גם מי טרם נערכה לו ישיבה.
        </p>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState error={error} />}
      {!isLoading && !error && isReady && (
        <Months items={overviewQuery.data} students={studentsQuery.data} />
      )}
    </div>
  );
}

function Months({
  items,
  students,
}: {
  items: MeetingOverviewItem[];
  students: StudentResponse[];
}): ReactNode {
  const now = new Date();
  const currentKey = now.getFullYear() * 100 + (now.getMonth() + 1);

  const groups = new Map<number, MonthGroup>();
  groups.set(currentKey, {
    key: currentKey,
    year: now.getFullYear(),
    month: now.getMonth() + 1,
    met: [],
  });
  for (const item of items) {
    const key = item.year * 100 + item.month;
    const group = groups.get(key) ?? { key, year: item.year, month: item.month, met: [] };
    if (!group.met.some((existing) => existing.student_id === item.student_id)) {
      group.met.push(item);
    }
    groups.set(key, group);
  }

  const ordered = [...groups.values()].sort((first, second) => second.key - first.key);
  const activeStudents = students.filter((student) => !student.is_archived);
  const metThisMonth = new Set(
    (groups.get(currentKey)?.met ?? []).map((item) => item.student_id)
  );
  const notMetThisMonth = activeStudents.filter(
    (student) => !metThisMonth.has(student.id)
  );

  return (
    <div className="space-y-4">
      {ordered.map((group) => (
        <Card key={group.key}>
          <CardHeader>
            <CardTitle>{formatMonthYear(group.year, group.month)}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <MetSection met={group.met} />
            {group.key === currentKey && <NotMetSection students={notMetThisMonth} />}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function MetSection({ met }: { met: MeetingOverviewItem[] }): ReactNode {
  return (
    <div>
      <div className="mb-2 text-sm font-medium text-brand">נערכה ישיבה</div>
      {met.length === 0 ? (
        <EmptyState>טרם נערכה ישיבה בחודש זה.</EmptyState>
      ) : (
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {met.map((item) => (
            <StudentLinkCard
              key={item.student_id}
              id={item.student_id}
              name={item.student_name}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function NotMetSection({ students }: { students: StudentResponse[] }): ReactNode {
  if (students.length === 0) {
    return null;
  }
  return (
    <div className="border-t border-slate-100 pt-4">
      <div className="mb-2 text-sm font-medium text-ink-muted">טרם נערכה ישיבה</div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {students.map((student) => (
          <StudentLinkCard key={student.id} id={student.id} name={student.full_name} />
        ))}
      </div>
    </div>
  );
}
