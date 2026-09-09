import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { taxonomyApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { LabelTreeNode, MeetingRating } from "@/lib/api/types";
import type { FocusDraft } from "@/lib/program/buildFoci";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, errorMessage } from "@/components/ui/ErrorState";
import { FocusRatingRow } from "@/pages/student/program/FocusRatingRow";

type SetDraft = (skillId: string, next: MeetingRating | null) => void;

export function FocusRatingTree({
  drafts,
  setDraft,
}: {
  drafts: FocusDraft;
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
  drafts: FocusDraft;
  setDraft: SetDraft;
}): ReactNode {
  return (
    <details className="rounded-lg border border-slate-200 bg-white">
      <summary className="cursor-pointer px-4 py-2.5 font-medium text-ink">
        {label.name}
      </summary>
      <div className="space-y-2 border-t border-slate-100 p-3">
        {label.skills.map((skill) => (
          <FocusRatingRow
            key={skill.id}
            skill={skill}
            rating={drafts[skill.id] ?? null}
            onChange={(next) => setDraft(skill.id, next)}
          />
        ))}
      </div>
    </details>
  );
}
