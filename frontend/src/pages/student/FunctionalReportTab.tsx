import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { detailsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { LoadingState } from "@/components/ui/Spinner";
import { ErrorState } from "@/components/ui/ErrorState";
import {
  CommunicationChannelCard,
  EmotionalProfileCard,
} from "@/pages/student/details/DetailProfileCards";

export function FunctionalReportTab({ studentId }: { studentId: string }): ReactNode {
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
      <p className="text-sm text-ink-muted">
        סיכום מתוך פרטי התלמיד. לעריכה יש לעבור לטאב פרטים אישיים.
      </p>
      <div className="grid gap-6 lg:grid-cols-2">
        <EmotionalProfileCard details={query.data} />
        <CommunicationChannelCard details={query.data} />
      </div>
    </div>
  );
}
