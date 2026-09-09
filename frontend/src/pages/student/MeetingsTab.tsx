import { useEffect, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus } from "lucide-react";
import { meetingsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { MeetingResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";
import { AddMeetingDialog } from "@/pages/student/meetings/AddMeetingDialog";
import { MeetingSnapshot } from "@/pages/student/meetings/MeetingSnapshot";

interface MeetingsTabProps {
  studentId: string;
  autoOpenNew?: boolean;
  onAutoOpenConsumed?: () => void;
}

export function MeetingsTab({
  studentId,
  autoOpenNew = false,
  onAutoOpenConsumed,
}: MeetingsTabProps): ReactNode {
  const { user } = useAuth();
  const [addOpen, setAddOpen] = useState(false);
  const canWrite = user ? permissions.canWriteMeetings(user) : false;

  useEffect(() => {
    if (autoOpenNew && canWrite) {
      setAddOpen(true);
      onAutoOpenConsumed?.();
    }
  }, [autoOpenNew, canWrite, onAutoOpenConsumed]);

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
            ישיבת צוות חדשה
          </Button>
        )}
      </div>

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data && (
        <MeetingList studentId={studentId} meetings={query.data} canWrite={canWrite} />
      )}

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
  canWrite,
}: {
  studentId: string;
  meetings: MeetingResponse[];
  canWrite: boolean;
}): ReactNode {
  if (meetings.length === 0) {
    return <EmptyState>אין ישיבות מתועדות עדיין.</EmptyState>;
  }

  return (
    <div className="space-y-6">
      {meetings.map((meeting) => (
        <Card key={meeting.id}>
          <CardHeader className="flex items-center justify-between">
            <CardTitle>{formatDate(meeting.meeting_date)}</CardTitle>
            <PdfButton
              url={meetingsApi.pdfUrl(studentId, meeting.id)}
              label="ייצוא PDF"
            />
          </CardHeader>
          <CardContent className="space-y-4">
            <MeetingSnapshot data={meeting} />
            <SummarySection studentId={studentId} meeting={meeting} canWrite={canWrite} />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

function SummarySection({
  studentId,
  meeting,
  canWrite,
}: {
  studentId: string;
  meeting: MeetingResponse;
  canWrite: boolean;
}): ReactNode {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(meeting.summary);

  const mutation = useMutation({
    mutationFn: () =>
      meetingsApi.updateSummary(studentId, meeting.id, { summary: draft }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.meetings(studentId) });
      setEditing(false);
    },
  });

  return (
    <div className="space-y-2 border-t border-slate-100 pt-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-ink">סיכום</h3>
        {canWrite && !editing && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setDraft(meeting.summary);
              setEditing(true);
            }}
          >
            <Pencil className="h-4 w-4" />
            עריכת סיכום
          </Button>
        )}
      </div>

      {editing ? (
        <div className="space-y-2">
          <Textarea
            className="min-h-40"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="סיכום הישיבה…"
          />
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          <div className="flex justify-end gap-2">
            <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
              {mutation.isPending ? "שומר…" : "שמירה"}
            </Button>
            <Button variant="ghost" onClick={() => setEditing(false)}>
              ביטול
            </Button>
          </div>
        </div>
      ) : meeting.summary.trim() ? (
        <p className="whitespace-pre-wrap text-sm text-ink">{meeting.summary}</p>
      ) : (
        <EmptyState>לא נכתב סיכום.</EmptyState>
      )}
    </div>
  );
}
