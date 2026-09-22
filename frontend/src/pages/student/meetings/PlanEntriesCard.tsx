import type { ReactNode } from "react";
import type { PlanEntryResponse } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";

export function PlanEntriesCard({
  entries,
}: {
  entries: PlanEntryResponse[];
}): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>תוכנית אישית</CardTitle>
      </CardHeader>
      <CardContent>
        {entries.length === 0 ? (
          <EmptyState>אין תוכנית אישית.</EmptyState>
        ) : (
          <ul className="space-y-3">
            {entries.map((entry) => (
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
  );
}
