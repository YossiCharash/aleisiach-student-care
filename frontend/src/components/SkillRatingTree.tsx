import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { taxonomyApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { LabelTreeNode } from "@/lib/api/types";
import type { EntryDraft } from "@/lib/meetings/buildEntries";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, errorMessage } from "@/components/ui/ErrorState";
import { SkillEntryRow } from "@/pages/student/meetings/SkillEntryRow";

type SetDraft = (skillId: string, next: EntryDraft | null) => void;

export function SkillRatingTree({
  drafts,
  setDraft,
}: {
  drafts: Record<string, EntryDraft>;
  setDraft: SetDraft;
}): ReactNode {
  const treeQuery = useQuery({
    queryKey: queryKeys.taxonomyTree,
    queryFn: taxonomyApi.tree,
  });

  if (treeQuery.isLoading) {
    return <LoadingState />;
  }
  if (treeQuery.isError) {
    return <Alert tone="error">{errorMessage(treeQuery.error)}</Alert>;
  }

  const tree = treeQuery.data ?? [];
  if (tree.length === 0) {
    return <EmptyState>לא הוגדרה טקסונומיה. יש להגדיר בהגדרות תחילה.</EmptyState>;
  }

  return (
    <div className="max-h-[45vh] space-y-2 overflow-y-auto pe-1">
      {tree.map((label) => (
        <LabelAccordion
          key={label.id}
          label={label}
          drafts={drafts}
          setDraft={setDraft}
        />
      ))}
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
  setDraft: SetDraft;
}): ReactNode {
  return (
    <details className="rounded-lg border border-slate-200 bg-white">
      <summary className="cursor-pointer px-4 py-2.5 font-medium text-ink">
        {label.name}
      </summary>
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
