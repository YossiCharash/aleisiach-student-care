import type { ReactNode } from "react";
import type { MeetingResponse } from "@/lib/api/types";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/ErrorState";
import { PlanEntriesCard } from "@/pages/student/meetings/MeetingSnapshot";

export function PreviousMeetingCard({
  meeting,
}: {
  meeting: MeetingResponse;
}): ReactNode {
  return (
    <Card className="border-slate-200 bg-slate-50">
      <CardHeader>
        <CardTitle>הישיבה הקודמת · {formatDate(meeting.meeting_date)}</CardTitle>
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
        <PlanEntriesCard entries={meeting.plan_entries} />
      </CardContent>
    </Card>
  );
}
