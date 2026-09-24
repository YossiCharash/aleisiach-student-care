import { useEffect, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus } from "lucide-react";
import { meetingsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { MeetingResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { formatDate } from "@/lib/utils/hebrew";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";
import { AddMeetingDialog } from "@/pages/student/meetings/AddMeetingDialog";
import { PlanEntriesCard } from "@/pages/student/meetings/PlanEntriesCard";
import { ParticipantsField } from "@/pages/student/meetings/ParticipantsField";

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
  const [selectedId, setSelectedId] = useState<string | null>(null);
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

  const selected = query.data?.find((meeting) => meeting.id === selectedId) ?? null;

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
      {query.data && <MeetingGrid meetings={query.data} onSelect={setSelectedId} />}

      {selected && (
        <MeetingDetailDialog
          studentId={studentId}
          meeting={selected}
          canWrite={canWrite}
          onOpenChange={() => setSelectedId(null)}
        />
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

function MeetingGrid({
  meetings,
  onSelect,
}: {
  meetings: MeetingResponse[];
  onSelect: (id: string) => void;
}): ReactNode {
  if (meetings.length === 0) {
    return <EmptyState>אין ישיבות מתועדות עדיין.</EmptyState>;
  }

  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(7rem,1fr))] gap-3">
      {meetings.map((meeting) => (
        <MeetingTile key={meeting.id} meeting={meeting} onSelect={onSelect} />
      ))}
    </div>
  );
}

function MeetingTile({
  meeting,
  onSelect,
}: {
  meeting: MeetingResponse;
  onSelect: (id: string) => void;
}): ReactNode {
  const [year, month, day] = meeting.meeting_date.split("-");

  return (
    <button
      type="button"
      onClick={() => onSelect(meeting.id)}
      className="flex aspect-square flex-col items-center justify-center rounded-xl border border-slate-200 bg-white text-ink shadow-sm transition-colors hover:border-brand-300 hover:bg-brand-soft focus:outline-none focus-visible:ring-2 focus-visible:ring-brand"
      aria-label={`ישיבת צוות מתאריך ${formatDate(meeting.meeting_date)}`}
    >
      <span className="tnum text-2xl font-bold leading-none">{day}</span>
      <span className="tnum mt-1 text-sm text-ink-muted">
        {month}/{year}
      </span>
    </button>
  );
}

function MeetingDetailDialog({
  studentId,
  meeting,
  canWrite,
  onOpenChange,
}: {
  studentId: string;
  meeting: MeetingResponse;
  canWrite: boolean;
  onOpenChange: (open: boolean) => void;
}): ReactNode {
  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <div className="flex items-center justify-between gap-4 pe-8">
            <DialogTitle>ישיבת צוות — {formatDate(meeting.meeting_date)}</DialogTitle>
            <PdfButton
              url={meetingsApi.pdfUrl(studentId, meeting.id)}
              label="ייצוא PDF"
            />
          </div>
        </DialogHeader>
        <div className="space-y-4">
          <ParticipantsSection meeting={meeting} />
          <PlanEntriesCard entries={meeting.plan_entries} />
          <SummarySection studentId={studentId} meeting={meeting} canWrite={canWrite} />
        </div>
      </DialogContent>
    </Dialog>
  );
}

function ParticipantsSection({ meeting }: { meeting: MeetingResponse }): ReactNode {
  return (
    <div className="space-y-1">
      <h3 className="font-semibold text-ink">משתתפים</h3>
      {meeting.participants.trim() ? (
        <p className="whitespace-pre-wrap text-sm text-ink">{meeting.participants}</p>
      ) : (
        <EmptyState>לא צוינו משתתפים.</EmptyState>
      )}
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
  const [summary, setSummary] = useState(meeting.summary);
  const [participants, setParticipants] = useState(meeting.participants);

  const mutation = useMutation({
    mutationFn: () =>
      meetingsApi.updateSummary(studentId, meeting.id, { participants, summary }),
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
              setSummary(meeting.summary);
              setParticipants(meeting.participants);
              setEditing(true);
            }}
          >
            <Pencil className="h-4 w-4" />
            עריכה
          </Button>
        )}
      </div>

      {editing ? (
        <div className="space-y-3">
          <ParticipantsField
            id={`meeting-participants-${meeting.id}`}
            value={participants}
            onChange={setParticipants}
          />
          <div className="space-y-1">
            <Label htmlFor={`meeting-summary-${meeting.id}`}>סיכום</Label>
            <Textarea
              id={`meeting-summary-${meeting.id}`}
              className="min-h-40"
              value={summary}
              onChange={(event) => setSummary(event.target.value)}
              placeholder="סיכום הישיבה…"
            />
          </div>
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
