import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Building2 } from "lucide-react";
import { institutionsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { InstitutionSummary } from "@/lib/api/types";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { CreateInstitutionDialog } from "@/pages/institutions/CreateInstitutionDialog";
import { InstitutionRow } from "@/pages/institutions/InstitutionRow";

export function InstitutionsPage(): ReactNode {
  const [createOpen, setCreateOpen] = useState(false);
  const query = useQuery({
    queryKey: queryKeys.institutions,
    queryFn: institutionsApi.list,
  });

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">ניהול מוסדות</h1>
          <p className="mt-1 text-sm text-ink-muted">
            כל מוסד מנהל את התלמידים, הצוות וההגדרות שלו בנפרד.
          </p>
        </div>
        <Button onClick={() => setCreateOpen(true)}>
          <Building2 className="h-4 w-4" />
          מוסד חדש
        </Button>
      </div>

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data && <InstitutionsTable institutions={query.data} />}

      <CreateInstitutionDialog open={createOpen} onOpenChange={setCreateOpen} />
    </div>
  );
}

function InstitutionsTable({
  institutions,
}: {
  institutions: InstitutionSummary[];
}): ReactNode {
  if (institutions.length === 0) {
    return <EmptyState>עדיין לא הוקם אף מוסד.</EmptyState>;
  }

  return (
    <Card>
      <CardContent className="p-0">
        <table className="w-full text-start text-sm">
          <thead className="border-b border-slate-100 text-ink-muted">
            <tr>
              <th className="px-4 py-3 text-start font-medium">שם המוסד</th>
              <th className="px-4 py-3 text-start font-medium">קוד</th>
              <th className="px-4 py-3 text-start font-medium">איש קשר</th>
              <th className="px-4 py-3 text-start font-medium">משתמשים</th>
              <th className="px-4 py-3 text-start font-medium">תלמידים</th>
              <th className="px-4 py-3 text-start font-medium">סטטוס</th>
              <th className="px-4 py-3 text-start font-medium">פעולות</th>
            </tr>
          </thead>
          <tbody>
            {institutions.map((institution) => (
              <InstitutionRow key={institution.id} institution={institution} />
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
