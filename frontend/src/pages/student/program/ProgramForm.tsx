import { useMemo, useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { programApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { MeetingRating, ProgramResponse } from "@/lib/api/types";
import { focusDraftsToEntries, type FocusDraft } from "@/lib/program/buildFoci";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import { FocusRatingTree } from "@/pages/student/program/FocusRatingTree";

function draftsFromProgram(program: ProgramResponse): FocusDraft {
  const drafts: FocusDraft = {};
  for (const entry of program.entries) {
    drafts[entry.skill_id] = entry.rating;
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
  const [drafts, setDrafts] = useState<FocusDraft>(() => draftsFromProgram(program));
  const [validationError, setValidationError] = useState<string | null>(null);

  const entries = useMemo(() => focusDraftsToEntries(drafts), [drafts]);

  const mutation = useMutation({
    mutationFn: () => programApi.upsert(studentId, { entries }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.program(studentId) });
      onDone();
    },
  });

  function setDraft(skillId: string, next: MeetingRating | null): void {
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
      setValidationError("יש לסמן דירוג לפחות לכישור אחד.");
      return;
    }
    mutation.mutate();
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-ink-muted">
        לכל כישור סמנו שורה אחת: ירוק = מוקד כוח, צהוב/אדום = מוקד לחיזוק. דרכי הפתרון
        נבחרות בהמשך בעת בניית התוכנית האישית.
      </p>

      {validationError && <Alert tone="error">{validationError}</Alert>}
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <FocusRatingTree drafts={drafts} setDraft={setDraft} />

      <div className="flex items-center justify-between border-t border-slate-100 pt-4">
        <span className="text-sm text-ink-muted">{entries.length} כישורים סומנו</span>
        <div className="flex gap-2">
          <Button onClick={handleSubmit} disabled={mutation.isPending}>
            {mutation.isPending ? "שומר…" : "שמירת מוקדים"}
          </Button>
          <Button variant="ghost" onClick={onDone}>
            ביטול
          </Button>
        </div>
      </div>
    </div>
  );
}
