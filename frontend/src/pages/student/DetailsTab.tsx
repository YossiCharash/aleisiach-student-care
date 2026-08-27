import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import { detailsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { ErrorState } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";
import { DetailsView } from "@/pages/student/details/DetailsView";
import { DetailsForm } from "@/pages/student/details/DetailsForm";

export function DetailsTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const [editing, setEditing] = useState(false);
  const canWrite = user ? permissions.canWriteDetails(user) : false;

  const query = useQuery({
    queryKey: queryKeys.details(studentId),
    queryFn: () => detailsApi.get(studentId),
  });

  if (query.isLoading) {
    return <LoadingState />;
  }
  if (query.isError) {
    return <ErrorState error={query.error} />;
  }
  if (!query.data) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <PdfButton url={detailsApi.pdfUrl(studentId)} label="ייצוא PDF" />
        {canWrite && !editing && (
          <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
            <Pencil className="h-4 w-4" />
            עריכה
          </Button>
        )}
      </div>

      {editing ? (
        <DetailsForm
          studentId={studentId}
          details={query.data}
          onDone={() => setEditing(false)}
        />
      ) : (
        <DetailsView details={query.data} />
      )}
    </div>
  );
}
