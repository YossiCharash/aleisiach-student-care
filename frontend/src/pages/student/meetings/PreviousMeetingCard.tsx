import { useState, type ReactNode } from "react";
import { FileText } from "lucide-react";
import type { MeetingResponse } from "@/lib/api/types";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/Dialog";
import { EmptyState } from "@/components/ui/ErrorState";
import { PlanEntriesCard } from "@/pages/student/meetings/PlanEntriesCard";

export function PreviousMeetingCard({
  meeting,
}: {
  meeting: MeetingResponse;
}): ReactNode {
  const [planOpen, setPlanOpen] = useState(false);
  const meetingDate = formatDate(meeting.meeting_date);

  return (
    <Card className="border-slate-200 bg-slate-50">
      <CardHeader>
        <CardTitle>הישיבה הקודמת · {meetingDate}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1">
          <h4 className="font-semibold text-ink">סיכום</h4>
          {meeting.summary.trim() ? (
            <p className="whitespace-pre-wrap text-sm text-ink">{meeting.summary}</p>
          ) : (
            <EmptyState>לא נכתב סיכום.</EmptyState>
          )}
        </div>
        <button
          type="button"
          onClick={() => setPlanOpen(true)}
          className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-700 underline underline-offset-4 hover:text-brand"
        >
          <FileText className="h-4 w-4" />
          התוכנית האישית בזמן הישיבה הקודמת
        </button>
      </CardContent>

      <Dialog open={planOpen} onOpenChange={setPlanOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>התוכנית האישית · הישיבה מיום {meetingDate}</DialogTitle>
          </DialogHeader>
          <PlanEntriesCard entries={meeting.plan_entries} />
        </DialogContent>
      </Dialog>
    </Card>
  );
}
