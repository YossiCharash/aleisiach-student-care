import { useMemo, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { programApi, programPlansApi, taxonomyApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { LabelTreeNode, ProgramArea, SolutionTreeNode } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";

type Selections = Record<string, string[]>;

function solutionsBySkill(tree: LabelTreeNode[]): Record<string, SolutionTreeNode[]> {
  const map: Record<string, SolutionTreeNode[]> = {};
  for (const label of tree) {
    for (const skill of label.skills) {
      map[skill.id] = skill.solutions;
    }
  }
  return map;
}

export function PlanForm({
  studentId,
  onDone,
}: {
  studentId: string;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [selections, setSelections] = useState<Selections>({});
  const [validationError, setValidationError] = useState<string | null>(null);

  const programQuery = useQuery({
    queryKey: queryKeys.program(studentId),
    queryFn: () => programApi.get(studentId),
  });
  const treeQuery = useQuery({
    queryKey: queryKeys.taxonomyTree,
    queryFn: taxonomyApi.tree,
  });

  const solutionsMap = useMemo(
    () => solutionsBySkill(treeQuery.data ?? []),
    [treeQuery.data]
  );

  const mutation = useMutation({
    mutationFn: () => {
      const entries = Object.entries(selections)
        .filter(([, ids]) => ids.length > 0)
        .map(([skillId, ids]) => ({ skill_id: skillId, solution_ids: ids }));
      return programPlansApi.create(studentId, { entries });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.programPlans(studentId) });
      onDone();
    },
  });

  if (programQuery.isLoading || treeQuery.isLoading) {
    return <LoadingState />;
  }
  if (programQuery.isError) {
    return <ErrorState error={programQuery.error} />;
  }
  if (treeQuery.isError) {
    return <ErrorState error={treeQuery.error} />;
  }

  const areas = programQuery.data?.areas_to_strengthen ?? [];
  if (areas.length === 0) {
    return (
      <div className="space-y-4">
        <EmptyState>
          אין מוקדים לחיזוק. יש לסמן מוקדים לחיזוק בתווית המוקדים לפני בניית תוכנית.
        </EmptyState>
        <Button variant="ghost" onClick={onDone}>
          חזרה
        </Button>
      </div>
    );
  }

  function toggle(skillId: string, solutionId: string): void {
    setValidationError(null);
    setSelections((current) => {
      const ids = current[skillId] ?? [];
      const next = ids.includes(solutionId)
        ? ids.filter((id) => id !== solutionId)
        : [...ids, solutionId];
      return { ...current, [skillId]: next };
    });
  }

  function handleSubmit(): void {
    const chosen = Object.values(selections).filter((ids) => ids.length > 0);
    if (chosen.length === 0) {
      setValidationError("יש לבחור דרך פתרון אחת לפחות עבור מוקד אחד.");
      return;
    }
    mutation.mutate();
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-ink-muted">
        בחרו את דרכי הפתרון לכל מוקד לחיזוק. התוכנית תישמר עם התאריך הנוכחי, והתוכנית
        הקודמת תיכנס להיסטוריה.
      </p>

      {validationError && <Alert tone="error">{validationError}</Alert>}
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <div className="space-y-3">
        {areas.map((area) => (
          <AreaSolutions
            key={area.skill_id}
            area={area}
            solutions={(solutionsMap[area.skill_id] ?? []).filter(
              (solution) => solution.rating === area.rating
            )}
            selected={selections[area.skill_id] ?? []}
            onToggle={(solutionId) => toggle(area.skill_id, solutionId)}
          />
        ))}
      </div>

      <div className="flex items-center justify-end gap-2 border-t border-slate-100 pt-4">
        <Button onClick={handleSubmit} disabled={mutation.isPending}>
          {mutation.isPending ? "שומר…" : "שמירת תוכנית"}
        </Button>
        <Button variant="ghost" onClick={onDone}>
          ביטול
        </Button>
      </div>
    </div>
  );
}

function AreaSolutions({
  area,
  solutions,
  selected,
  onToggle,
}: {
  area: ProgramArea;
  solutions: SolutionTreeNode[];
  selected: string[];
  onToggle: (solutionId: string) => void;
}): ReactNode {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="font-semibold text-ink">{area.skill_name}</span>
        <RatingPill rating={area.rating} />
      </div>
      {solutions.length === 0 ? (
        <p className="text-xs text-ink-muted">אין דרכי פתרון מוגדרות לכישור זה.</p>
      ) : (
        <div className="space-y-1">
          {solutions.map((solution) => (
            <label key={solution.id} className="flex items-center gap-2 text-sm text-ink">
              <input
                type="checkbox"
                checked={selected.includes(solution.id)}
                onChange={() => onToggle(solution.id)}
                className="h-4 w-4 accent-brand"
              />
              {solution.text}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
