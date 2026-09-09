import type { ReactNode } from "react";
import type { PlanEntryResponse, ProgramArea, ProgramStrength } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";

export interface MeetingSnapshotData {
  strengths: ProgramStrength[];
  areas_to_strengthen: ProgramArea[];
  plan_entries: PlanEntryResponse[];
}

export function MeetingSnapshot({ data }: { data: MeetingSnapshotData }): ReactNode {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>מוקדי כוח</CardTitle>
          </CardHeader>
          <CardContent>
            {data.strengths.length === 0 ? (
              <EmptyState>אין מוקדי כוח.</EmptyState>
            ) : (
              <ul className="space-y-2">
                {data.strengths.map((strength) => (
                  <li
                    key={strength.skill_id}
                    className="rounded-xl border-s-4 border-rating-green bg-accent-50 px-3.5 py-2.5 font-medium text-brand-700"
                  >
                    {strength.skill_name}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>מוקדים לחיזוק</CardTitle>
          </CardHeader>
          <CardContent>
            {data.areas_to_strengthen.length === 0 ? (
              <EmptyState>אין מוקדים לחיזוק.</EmptyState>
            ) : (
              <ul className="space-y-2">
                {data.areas_to_strengthen.map((area) => (
                  <li
                    key={area.skill_id}
                    className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 px-3.5 py-2.5"
                  >
                    <span className="font-medium text-ink">{area.skill_name}</span>
                    <RatingPill rating={area.rating} />
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>תוכנית אישית</CardTitle>
        </CardHeader>
        <CardContent>
          {data.plan_entries.length === 0 ? (
            <EmptyState>אין תוכנית אישית.</EmptyState>
          ) : (
            <ul className="space-y-3">
              {data.plan_entries.map((entry) => (
                <li
                  key={entry.skill_id}
                  className="rounded-xl border border-slate-200 px-3.5 py-2.5"
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
                        <li key={solution.solution_id}>
                          {solution.solution_text_snapshot}
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
