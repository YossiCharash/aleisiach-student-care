import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { History, Plus } from "lucide-react";
import { programPlansApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { PlanResponse } from "@/lib/api/types";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";
import { PdfButton } from "@/components/PdfButton";
import { PlanForm } from "@/pages/student/program/PlanForm";

export function PersonalPlanTab({
  studentId,
  canWrite,
}: {
  studentId: string;
  canWrite: boolean;
}): ReactNode {
  const [creating, setCreating] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.programPlans(studentId),
    queryFn: () => programPlansApi.list(studentId),
  });

  if (creating) {
    return <PlanForm studentId={studentId} onDone={() => setCreating(false)} />;
  }
  if (query.isLoading) {
    return <LoadingState />;
  }
  if (query.isError) {
    return <ErrorState error={query.error} />;
  }

  const plans = query.data ?? [];
  const [latest, ...history] = plans;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-2">
          {plans.length > 0 && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowHistory((value) => !value)}
              >
                <History className="h-4 w-4" />
                {showHistory ? "הסתרת היסטוריה" : "היסטוריה"}
              </Button>
              <PdfButton
                url={programPlansApi.combinedPdfUrl(studentId)}
                label="דוח כל התאריכים"
              />
            </>
          )}
        </div>
        {canWrite && (
          <Button onClick={() => setCreating(true)}>
            <Plus className="h-4 w-4" />
            יצירת תוכנית
          </Button>
        )}
      </div>

      {plans.length === 0 ? (
        <EmptyState>אין עדיין תוכנית אישית לתלמיד.</EmptyState>
      ) : (
        <div className="space-y-4">
          <PlanCard studentId={studentId} plan={latest} isLatest />
          {showHistory &&
            history.map((plan) => (
              <PlanCard
                key={plan.id}
                studentId={studentId}
                plan={plan}
                isLatest={false}
              />
            ))}
        </div>
      )}
    </div>
  );
}

function PlanCard({
  studentId,
  plan,
  isLatest,
}: {
  studentId: string;
  plan: PlanResponse;
  isLatest: boolean;
}): ReactNode {
  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <CardTitle className="flex items-center gap-2.5">
          {formatDate(plan.created_at)}
          {isLatest && (
            <span className="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-semibold text-brand-700">
              עדכנית
            </span>
          )}
        </CardTitle>
        <PdfButton url={programPlansApi.pdfUrl(studentId, plan.id)} label="ייצוא PDF" />
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {plan.entries.map((entry) => (
            <li
              key={entry.skill_id}
              className="rounded-xl border border-slate-200 px-3.5 py-3"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="font-semibold text-ink">
                  {entry.skill_name_snapshot}
                </span>
                <RatingPill rating={entry.rating} />
              </div>
              {entry.solutions.length > 0 && (
                <ul className="mt-2 list-disc space-y-1 pe-5 text-sm text-ink-muted">
                  {entry.solutions.map((solution) => (
                    <li key={solution.solution_id}>{solution.solution_text_snapshot}</li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
