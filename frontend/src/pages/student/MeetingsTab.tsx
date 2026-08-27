import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { meetingsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { MeetingResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { formatMonthYear } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";
import { PdfButton } from "@/components/PdfButton";
import { AddMeetingDialog } from "@/pages/student/meetings/AddMeetingDialog";

export function MeetingsTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const [addOpen, setAddOpen] = useState(false);
  const canWrite = user ? permissions.canWriteMeetings(user) : false;

  const query = useQuery({
    queryKey: queryKeys.meetings(studentId),
    queryFn: () => meetingsApi.list(studentId),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">ישיבות צוות</h2>
        {canWrite && (
          <Button onClick={() => setAddOpen(true)}>
            <Plus className="h-4 w-4" />
            ישיבה חודשית חדשה
          </Button>
        )}
      </div>

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data && <MeetingList studentId={studentId} meetings={query.data} />}

      {canWrite && (
        <AddMeetingDialog
          studentId={studentId}
          open={addOpen}
          onOpenChange={setAddOpen}
        />
      )}
    </div>
  );
}

function MeetingList({
  studentId,
  meetings,
}: {
  studentId: string;
  meetings: MeetingResponse[];
}): ReactNode {
  if (meetings.length === 0) {
    return <EmptyState>אין ישיבות מתועדות עדיין.</EmptyState>;
  }

  const sorted = [...meetings].sort((first, second) => {
    if (first.year !== second.year) {
      return second.year - first.year;
    }
    return second.month - first.month;
  });

  return (
    <div className="space-y-4">
      {sorted.map((meeting) => (
        <Card key={meeting.id}>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>{formatMonthYear(meeting.year, meeting.month)}</CardTitle>
            <PdfButton
              url={meetingsApi.pdfUrl(studentId, meeting.id)}
              label="ייצוא PDF"
            />
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {meeting.entries.map((entry) => (
                <li
                  key={entry.id}
                  className="rounded-lg border border-slate-100 px-3 py-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-ink">
                      {entry.skill_name_snapshot}
                    </span>
                    <RatingPill rating={entry.rating} />
                  </div>
                  {entry.solutions.length > 0 && (
                    <ul className="mt-1.5 list-disc space-y-0.5 pe-5 text-sm text-ink-muted">
                      {entry.solutions.map((solution) => (
                        <li key={solution.id}>{solution.solution_text_snapshot}</li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
