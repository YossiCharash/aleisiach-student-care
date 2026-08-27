import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { programApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ProgramArea, ProgramStrength } from "@/lib/api/types";
import { formatMonthYear } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";

export function ProgramTab({ studentId }: { studentId: string }): ReactNode {
  const query = useQuery({
    queryKey: queryKeys.program(studentId),
    queryFn: () => programApi.get(studentId),
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

  const { strengths, areas_to_strengthen: areas } = query.data;

  return (
    <div className="space-y-6">
      <p className="text-sm text-ink-muted">
        התוכנית נגזרת אוטומטית מהדירוג האחרון של כל כישור בישיבות הצוות. אין לערוך כאן ידנית.
      </p>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>תחומי חוזק</CardTitle>
          </CardHeader>
          <CardContent>
            {strengths.length === 0 ? (
              <EmptyState>אין עדיין תחומי חוזק מתועדים.</EmptyState>
            ) : (
              <ul className="space-y-2">
                {strengths.map((strength) => (
                  <StrengthRow key={strength.skill_id} strength={strength} />
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>תחומים לחיזוק</CardTitle>
          </CardHeader>
          <CardContent>
            {areas.length === 0 ? (
              <EmptyState>אין עדיין תחומים לחיזוק.</EmptyState>
            ) : (
              <ul className="space-y-3">
                {areas.map((area) => (
                  <AreaRow key={area.skill_id} area={area} />
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StrengthRow({ strength }: { strength: ProgramStrength }): ReactNode {
  return (
    <li className="flex items-center justify-between rounded-lg bg-accent-50/60 px-3 py-2">
      <span className="font-medium text-ink">{strength.skill_name}</span>
      <span className="text-xs text-ink-muted">
        {formatMonthYear(strength.year, strength.month)}
      </span>
    </li>
  );
}

function AreaRow({ area }: { area: ProgramArea }): ReactNode {
  return (
    <li className="rounded-lg border border-slate-100 px-3 py-2">
      <div className="flex items-center justify-between">
        <span className="font-medium text-ink">{area.skill_name}</span>
        <RatingPill rating={area.rating} />
      </div>
      {area.solutions.length > 0 && (
        <div className="mt-2">
          <div className="mb-1 text-xs font-medium text-ink-muted">דרך לפתרון:</div>
          <ul className="list-disc space-y-0.5 pe-5 text-sm text-ink">
            {area.solutions.map((solution, index) => (
              <li key={index}>{solution}</li>
            ))}
          </ul>
        </div>
      )}
      <div className="mt-1 text-xs text-ink-muted">
        עודכן: {formatMonthYear(area.year, area.month)}
      </div>
    </li>
  );
}
