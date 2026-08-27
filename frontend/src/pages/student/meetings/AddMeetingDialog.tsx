import { useMemo, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { meetingsApi, taxonomyApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { LabelTreeNode } from "@/lib/api/types";
import { draftsToEntries, type EntryDraft } from "@/lib/meetings/buildEntries";
import { monthName } from "@/lib/utils/hebrew";
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
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, errorMessage } from "@/components/ui/ErrorState";
import { SkillEntryRow } from "@/pages/student/meetings/SkillEntryRow";

interface Props {
  studentId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AddMeetingDialog({ studentId, open, onOpenChange }: Props): ReactNode {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>ישיבה חודשית חדשה</DialogTitle>
          <DialogDescription>
            בחרו חודש, ולכל כישור קבעו דירוג. באדום/צהוב ניתן לבחור פתרונות.
          </DialogDescription>
        </DialogHeader>
        {open && <AddMeetingForm studentId={studentId} onDone={() => onOpenChange(false)} />}
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
  const [year, setYear] = useState(() => new Date().getFullYear());
  const [month, setMonth] = useState(() => new Date().getMonth() + 1);
  const [drafts, setDrafts] = useState<Record<string, EntryDraft>>({});
  const [validationError, setValidationError] = useState<string | null>(null);

  const treeQuery = useQuery({ queryKey: queryKeys.taxonomyTree, queryFn: taxonomyApi.tree });

  const entries = useMemo(() => draftsToEntries(drafts), [drafts]);

  const mutation = useMutation({
    mutationFn: () => meetingsApi.create(studentId, { year, month, entries }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.meetings(studentId) });
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

  if (treeQuery.isLoading) {
    return <LoadingState />;
  }
  if (treeQuery.isError) {
    return <Alert tone="error">{errorMessage(treeQuery.error)}</Alert>;
  }

  const tree = treeQuery.data ?? [];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <Label htmlFor="meeting-month">חודש</Label>
          <select
            id="meeting-month"
            value={month}
            onChange={(event) => setMonth(Number(event.target.value))}
            className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm"
          >
            {Array.from({ length: 12 }, (_, index) => index + 1).map((value) => (
              <option key={value} value={value}>
                {monthName(value)}
              </option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="meeting-year">שנה</Label>
          <Input
            id="meeting-year"
            type="number"
            min={2000}
            max={2100}
            value={year}
            onChange={(event) => setYear(Number(event.target.value))}
          />
        </div>
      </div>

      {validationError && <Alert tone="error">{validationError}</Alert>}
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <div className="max-h-[45vh] space-y-2 overflow-y-auto pe-1">
        {tree.length === 0 ? (
          <EmptyState>לא הוגדרה טקסונומיה. יש להגדיר בהגדרות תחילה.</EmptyState>
        ) : (
          tree.map((label) => (
            <LabelAccordion key={label.id} label={label} drafts={drafts} setDraft={setDraft} />
          ))
        )}
      </div>

      <div className="flex items-center justify-between border-t border-slate-100 pt-4">
        <span className="text-sm text-ink-muted">{entries.length} כישורים דורגו</span>
        <div className="flex gap-2">
          <Button onClick={handleSubmit} disabled={mutation.isPending}>
            {mutation.isPending ? "שומר…" : "שמירת ישיבה"}
          </Button>
          <Button variant="ghost" onClick={onDone}>
            ביטול
          </Button>
        </div>
      </div>
    </div>
  );
}

function LabelAccordion({
  label,
  drafts,
  setDraft,
}: {
  label: LabelTreeNode;
  drafts: Record<string, EntryDraft>;
  setDraft: (skillId: string, next: EntryDraft | null) => void;
}): ReactNode {
  return (
    <details className="rounded-lg border border-slate-200 bg-white">
      <summary className="cursor-pointer px-4 py-2.5 font-medium text-ink">{label.name}</summary>
      <div className="space-y-2 border-t border-slate-100 p-3">
        {label.sub_labels.map((subLabel) => (
          <div key={subLabel.id} className="rounded-lg bg-slate-50 p-3">
            <div className="mb-2 text-sm font-medium text-ink-muted">{subLabel.name}</div>
            <div className="space-y-2">
              {subLabel.skills.map((skill) => (
                <SkillEntryRow
                  key={skill.id}
                  skill={skill}
                  draft={drafts[skill.id] ?? null}
                  onChange={(next) => setDraft(skill.id, next)}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </details>
  );
}
