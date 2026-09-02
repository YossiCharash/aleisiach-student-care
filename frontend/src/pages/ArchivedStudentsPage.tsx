import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, RotateCcw } from "lucide-react";
import { studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { StudentResponse } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";

export function ArchivedStudentsPage(): ReactNode {
  const query = useQuery({
    queryKey: queryKeys.archivedStudents,
    queryFn: studentsApi.listArchived,
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">תלמידים בארכיון</h1>
          <p className="mt-1 text-sm text-ink-muted">
            תלמידים שהועברו לארכיון. ניתן לשחזר אותם לרשימה הפעילה.
          </p>
        </div>
        <Button asChild variant="ghost" size="sm">
          <Link to="/students">
            <ArrowRight className="h-4 w-4" />
            חזרה לתלמידים
          </Link>
        </Button>
      </div>

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data &&
        (query.data.length === 0 ? (
          <EmptyState>אין תלמידים בארכיון.</EmptyState>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {query.data.map((student) => (
              <ArchivedStudentCard key={student.id} student={student} />
            ))}
          </div>
        ))}
    </div>
  );
}

function ArchivedStudentCard({ student }: { student: StudentResponse }): ReactNode {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => studentsApi.restore(student.id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.students });
    },
  });

  return (
    <Card className="flex items-center justify-between px-5 py-4">
      <span className="font-medium text-ink">{student.full_name}</span>
      <Button
        variant="outline"
        size="sm"
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending}
      >
        <RotateCcw className="h-4 w-4" />
        {mutation.isPending ? "משחזר…" : "שחזור"}
      </Button>
    </Card>
  );
}
