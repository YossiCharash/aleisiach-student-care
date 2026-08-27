import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { taxonomyApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { LabelTreeNode, SkillTreeNode, SubLabelTreeNode } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";

export function TaxonomyArea(): ReactNode {
  const query = useQuery({ queryKey: queryKeys.taxonomyTree, queryFn: taxonomyApi.tree });

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-ink">טקסונומיה</h2>
        <p className="mt-1 text-sm text-ink-muted">
          תוויות ← תת-תוויות ← כישורים ← פתרונות. שינויים משתקפים מיד בטופס הישיבות.
        </p>
      </div>

      <AddInline
        placeholder="שם תווית חדשה"
        buttonLabel="הוספת תווית"
        onSubmit={(name) => taxonomyApi.createLabel(name)}
      />

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data &&
        (query.data.length === 0 ? (
          <EmptyState>אין תוויות עדיין.</EmptyState>
        ) : (
          <div className="space-y-2">
            {query.data.map((label) => (
              <LabelNode key={label.id} label={label} />
            ))}
          </div>
        ))}
    </div>
  );
}

function LabelNode({ label }: { label: LabelTreeNode }): ReactNode {
  return (
    <details className="rounded-lg border border-slate-200 bg-white">
      <summary className="cursor-pointer px-4 py-2.5 font-medium text-ink">{label.name}</summary>
      <div className="space-y-2 border-t border-slate-100 p-3">
        <AddInline
          placeholder="שם תת-תווית"
          buttonLabel="הוספת תת-תווית"
          onSubmit={(name) => taxonomyApi.createSubLabel(label.id, name)}
        />
        {label.sub_labels.map((subLabel) => (
          <SubLabelNode key={subLabel.id} subLabel={subLabel} />
        ))}
      </div>
    </details>
  );
}

function SubLabelNode({ subLabel }: { subLabel: SubLabelTreeNode }): ReactNode {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <div className="mb-2 text-sm font-medium text-ink-muted">{subLabel.name}</div>
      <AddInline
        placeholder="שם כישור"
        buttonLabel="הוספת כישור"
        onSubmit={(name) => taxonomyApi.createSkill(subLabel.id, name)}
      />
      <div className="mt-2 space-y-2">
        {subLabel.skills.map((skill) => (
          <SkillNode key={skill.id} skill={skill} />
        ))}
      </div>
    </div>
  );
}

function SkillNode({ skill }: { skill: SkillTreeNode }): ReactNode {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <div className="mb-2 text-sm font-medium text-ink">{skill.name}</div>
      <AddInline
        placeholder="טקסט פתרון"
        buttonLabel="הוספת פתרון"
        onSubmit={(text) => taxonomyApi.createSolution(skill.id, text)}
      />
      {skill.solutions.length > 0 && (
        <ul className="mt-2 list-disc space-y-0.5 pe-5 text-sm text-ink-muted">
          {skill.solutions.map((solution) => (
            <li key={solution.id}>{solution.text}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function AddInline({
  placeholder,
  buttonLabel,
  onSubmit,
}: {
  placeholder: string;
  buttonLabel: string;
  onSubmit: (value: string) => Promise<unknown>;
}): ReactNode {
  const queryClient = useQueryClient();
  const [value, setValue] = useState("");

  const mutation = useMutation({
    mutationFn: () => onSubmit(value.trim()),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.taxonomyTree });
      setValue("");
    },
  });

  return (
    <div className="flex items-center gap-2">
      <Input
        value={value}
        placeholder={placeholder}
        onChange={(event) => setValue(event.target.value)}
        className="h-9"
      />
      <Button
        type="button"
        size="sm"
        variant="outline"
        disabled={value.trim() === "" || mutation.isPending}
        onClick={() => mutation.mutate()}
      >
        <Plus className="h-4 w-4" />
        {buttonLabel}
      </Button>
    </div>
  );
}
