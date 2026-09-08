import { useMemo, useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { programApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ProgramResponse } from "@/lib/api/types";
import { draftsToEntries, type EntryDraft } from "@/lib/meetings/buildEntries";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import { SkillRatingTree } from "@/components/SkillRatingTree";

function draftsFromProgram(program: ProgramResponse): Record<string, EntryDraft> {
  const drafts: Record<string, EntryDraft> = {};
  for (const entry of program.entries) {
    drafts[entry.skill_id] = {
      rating: entry.rating,
      solutionIds: entry.solutions.map((solution) => solution.solution_id),
    };
  }
  return drafts;
}

export function ProgramForm({
  studentId,
  program,
  onDone,
}: {
  studentId: string;
  program: ProgramResponse;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [drafts, setDrafts] = useState<Record<string, EntryDraft>>(() =>
    draftsFromProgram(program)
  );
  const [validationError, setValidationError] = useState<string | null>(null);

  const entries = useMemo(() => draftsToEntries(drafts), [drafts]);

  const mutation = useMutation({
    mutationFn: () => programApi.upsert(studentId, { entries }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.program(studentId) });
      onDone();
    },
  });

  function setDraft(skillId: string, next: EntryDraft | null): void {
    setValidationError(null);
    setDrafts((current) => {
      const updated = { ...current };
      if (next === null) {
        delete updated[skillId];
      } else {
        updated[skillId] = next;
      }
      return updated;
    });
  }

  function handleSubmit(): void {
    if (entries.length === 0) {
      setValidationError("יש לדרג לפחות כישור אחד.");
      return;
    }
    mutation.mutate();
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-ink-muted">
        לכל כישור קבעו דירוג: ירוק = מוקד כוח, צהוב/אדום = מוקד לחיזוק. במוקד לחיזוק בחרו
        את דרכי הפתרון לתוכנית האישית.
      </p>

      {validationError && <Alert tone="error">{validationError}</Alert>}
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <SkillRatingTree drafts={drafts} setDraft={setDraft} />

      <div className="flex items-center justify-between border-t border-slate-100 pt-4">
        <span className="text-sm text-ink-muted">{entries.length} כישורים דורגו</span>
        <div className="flex gap-2">
          <Button onClick={handleSubmit} disabled={mutation.isPending}>
            {mutation.isPending ? "שומר…" : "שמירת תוכנית"}
          </Button>
          <Button variant="ghost" onClick={onDone}>
            ביטול
          </Button>
        </div>
      </div>
    </div>
  );
}
