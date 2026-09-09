import { useState, type ReactNode } from "react";
import { useMutation, useQueries, useQueryClient } from "@tanstack/react-query";
import { meetingsApi, programApi, programPlansApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { MeetingSnapshot } from "@/pages/student/meetings/MeetingSnapshot";

interface Props {
  studentId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

function today(): string {
  return new Date().toISOString().slice(0, 10);
}

export function AddMeetingDialog({ studentId, open, onOpenChange }: Props): ReactNode {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>ישיבת צוות חדשה</DialogTitle>
          <DialogDescription>
            מוקדי הכוח והמוקדים לחיזוק והתוכנית האישית מוצגים לקריאה בלבד ויישמרו כפי שהם כעת.
            מלאו את הסיכום.
          </DialogDescription>
        </DialogHeader>
        {open && (
          <AddMeetingForm studentId={studentId} onDone={() => onOpenChange(false)} />
        )}
      </DialogContent>
    </Dialog>
  );
}

function AddMeetingForm({
  studentId,
  onDone,
}: {
  studentId: string;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [meetingDate, setMeetingDate] = useState(today);
  const [summary, setSummary] = useState("");

  const [programQuery, plansQuery] = useQueries({
    queries: [
      {
        queryKey: queryKeys.program(studentId),
        queryFn: () => programApi.get(studentId),
      },
      {
        queryKey: queryKeys.programPlans(studentId),
        queryFn: () => programPlansApi.list(studentId),
      },
    ],
  });

  const mutation = useMutation({
    mutationFn: () => meetingsApi.create(studentId, { meeting_date: meetingDate, summary }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.meetings(studentId) });
      onDone();
    },
  });

  if (programQuery.isLoading || plansQuery.isLoading) {
    return <LoadingState />;
  }
  if (programQuery.isError) {
    return <ErrorState error={programQuery.error} />;
  }
  if (plansQuery.isError) {
    return <ErrorState error={plansQuery.error} />;
  }

  const program = programQuery.data;
  const latestPlan = plansQuery.data?.[0];
  const snapshot = {
    strengths: program?.strengths ?? [],
    areas_to_strengthen: program?.areas_to_strengthen ?? [],
    plan_entries: latestPlan?.entries ?? [],
  };

  return (
    <div className="space-y-4">
      <div className="max-w-xs">
        <Label htmlFor="meeting-date">תאריך הישיבה</Label>
        <Input
          id="meeting-date"
          type="date"
          value={meetingDate}
          onChange={(event) => setMeetingDate(event.target.value)}
        />
      </div>

      <MeetingSnapshot data={snapshot} />

      <div>
        <Label htmlFor="meeting-summary">סיכום</Label>
        <Textarea
          id="meeting-summary"
          className="min-h-40"
          value={summary}
          onChange={(event) => setSummary(event.target.value)}
          placeholder="סיכום הישיבה…"
        />
      </div>

      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <div className="flex items-center justify-end gap-2 border-t border-slate-100 pt-4">
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          {mutation.isPending ? "שומר…" : "שמירת ישיבה"}
        </Button>
        <Button variant="ghost" onClick={onDone}>
          ביטול
        </Button>
      </div>
    </div>
  );
}
