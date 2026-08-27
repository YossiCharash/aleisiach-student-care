import { useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, Plus } from "lucide-react";
import { studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { StudentResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { CreateStudentDialog } from "@/pages/students/CreateStudentDialog";

export function StudentsPage(): ReactNode {
  const { user } = useAuth();
  const [createOpen, setCreateOpen] = useState(false);
  const query = useQuery({ queryKey: queryKeys.students, queryFn: studentsApi.list });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">התלמידים שלי</h1>
          <p className="mt-1 text-sm text-ink-muted">
            שלום {user?.full_name}. לחצו על תלמיד לצפייה בתיק.
          </p>
        </div>
        {user && permissions.canCreateStudents(user) && (
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" />
            תלמיד חדש
          </Button>
        )}
      </div>

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data && <StudentList students={query.data} />}

      {user && permissions.canCreateStudents(user) && (
        <CreateStudentDialog open={createOpen} onOpenChange={setCreateOpen} />
      )}
    </div>
  );
}

function StudentList({ students }: { students: StudentResponse[] }): ReactNode {
  if (students.length === 0) {
    return <EmptyState>אין תלמידים להצגה עדיין.</EmptyState>;
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {students.map((student) => (
        <Link key={student.id} to={`/students/${student.id}`}>
          <Card className="flex items-center justify-between px-5 py-4 transition-colors hover:border-brand-300 hover:bg-brand-50/40">
            <span className="font-medium text-ink">{student.full_name}</span>
            <ChevronLeft className="h-5 w-5 text-slate-400" />
          </Card>
        </Link>
      ))}
    </div>
  );
}
