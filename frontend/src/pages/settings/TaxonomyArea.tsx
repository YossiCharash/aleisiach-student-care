import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, ChevronDown, Pencil, Plus, RotateCcw, Trash2, X } from "lucide-react";
import { taxonomyApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { LabelTreeNode, SkillTreeNode, SubLabelTreeNode } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";

function useTreeMutation<TArgs>(
  mutationFn: (args: TArgs) => Promise<unknown>
): (args: TArgs) => Promise<unknown> {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.taxonomyTree });
      void queryClient.invalidateQueries({ queryKey: queryKeys.taxonomyLabels });
    },
  });
  return mutation.mutateAsync;
}

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

      <InactiveLabels />
    </div>
  );
}

function LabelNode({ label }: { label: LabelTreeNode }): ReactNode {
  const [open, setOpen] = useState(false);
  const rename = useTreeMutation((name: string) =>
    taxonomyApi.updateLabel(label.id, { name })
  );
  const deactivate = useTreeMutation(() =>
    taxonomyApi.updateLabel(label.id, { is_active: false })
  );

  return (
    <div className="rounded-lg border border-slate-200 bg-white">
      <div className="flex items-center gap-2 px-3 py-2.5">
        <button
          type="button"
          onClick={() => setOpen((value) => !value)}
          className="text-ink-muted transition-transform"
          aria-label={open ? "כווץ" : "הרחב"}
          aria-expanded={open}
        >
          <ChevronDown className={`h-4 w-4 ${open ? "" : "-rotate-90"}`} />
        </button>
        <NodeName
          name={label.name}
          className="font-medium text-ink"
          onRename={(name) => rename(name)}
          onDeactivate={() => deactivate(undefined)}
          confirmLabel="להשבית את התווית וכל תוכנה?"
        />
      </div>
      {open && (
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
      )}
    </div>
  );
}

function SubLabelNode({ subLabel }: { subLabel: SubLabelTreeNode }): ReactNode {
  const rename = useTreeMutation((name: string) =>
    taxonomyApi.updateSubLabel(subLabel.id, { name })
  );
  const deactivate = useTreeMutation(() =>
    taxonomyApi.updateSubLabel(subLabel.id, { is_active: false })
  );

  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <NodeName
        name={subLabel.name}
        className="text-sm font-medium text-ink-muted"
        onRename={(name) => rename(name)}
        onDeactivate={() => deactivate(undefined)}
        confirmLabel="להשבית את תת-התווית?"
      />
      <div className="mt-2">
        <AddInline
          placeholder="שם כישור"
          buttonLabel="הוספת כישור"
          onSubmit={(name) => taxonomyApi.createSkill(subLabel.id, name)}
        />
      </div>
      <div className="mt-2 space-y-2">
        {subLabel.skills.map((skill) => (
          <SkillNode key={skill.id} skill={skill} />
        ))}
      </div>
    </div>
  );
}

function SkillNode({ skill }: { skill: SkillTreeNode }): ReactNode {
  const rename = useTreeMutation((name: string) =>
    taxonomyApi.updateSkill(skill.id, { name })
  );
  const deactivate = useTreeMutation(() =>
    taxonomyApi.updateSkill(skill.id, { is_active: false })
  );

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <NodeName
        name={skill.name}
        className="text-sm font-medium text-ink"
        onRename={(name) => rename(name)}
        onDeactivate={() => deactivate(undefined)}
        confirmLabel="להשבית את הכישור?"
      />
      <div className="mt-2">
        <AddInline
          placeholder="טקסט פתרון"
          buttonLabel="הוספת פתרון"
          onSubmit={(text) => taxonomyApi.createSolution(skill.id, text)}
        />
      </div>
      {skill.solutions.length > 0 && (
        <ul className="mt-2 space-y-1 text-sm text-ink-muted">
          {skill.solutions.map((solution) => (
            <SolutionRow key={solution.id} id={solution.id} text={solution.text} />
          ))}
        </ul>
      )}
    </div>
  );
}

function SolutionRow({ id, text }: { id: string; text: string }): ReactNode {
  const rename = useTreeMutation((next: string) =>
    taxonomyApi.updateSolution(id, { text: next })
  );
  const deactivate = useTreeMutation(() =>
    taxonomyApi.updateSolution(id, { is_active: false })
  );

  return (
    <li>
      <NodeName
        name={text}
        className="text-sm text-ink-muted"
        onRename={(next) => rename(next)}
        onDeactivate={() => deactivate(undefined)}
        confirmLabel="להשבית את הפתרון?"
      />
    </li>
  );
}

function InactiveLabels(): ReactNode {
  const [open, setOpen] = useState(false);
  const query = useQuery({
    queryKey: queryKeys.taxonomyLabels,
    queryFn: () => taxonomyApi.listLabels(true),
    enabled: open,
  });
  const reactivate = useTreeMutation((labelId: string) =>
    taxonomyApi.updateLabel(labelId, { is_active: true })
  );

  const inactive = (query.data ?? []).filter((label) => !label.is_active);

  return (
    <div className="border-t border-slate-100 pt-3">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex items-center gap-1.5 text-sm text-ink-muted hover:text-ink"
        aria-expanded={open}
      >
        <ChevronDown className={`h-4 w-4 ${open ? "" : "-rotate-90"}`} />
        תוויות מושבתות
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          {query.isLoading && <LoadingState />}
          {query.isError && <ErrorState error={query.error} />}
          {query.data &&
            (inactive.length === 0 ? (
              <EmptyState>אין תוויות מושבתות.</EmptyState>
            ) : (
              inactive.map((label) => (
                <div
                  key={label.id}
                  className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2"
                >
                  <span className="text-sm text-ink-muted">{label.name}</span>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void reactivate(label.id)}
                  >
                    <RotateCcw className="h-4 w-4" />
                    הפעלה מחדש
                  </Button>
                </div>
              ))
            ))}
          <p className="text-xs text-ink-muted">
            הפעלה מחדש של תת-תוויות, כישורים ופתרונות תתאפשר כשיתווסף שירות שליפה בצד
            השרת.
          </p>
        </div>
      )}
    </div>
  );
}

function NodeName({
  name,
  className,
  onRename,
  onDeactivate,
  confirmLabel,
}: {
  name: string;
  className?: string;
  onRename: (name: string) => Promise<unknown>;
  onDeactivate: () => Promise<unknown>;
  confirmLabel: string;
}): ReactNode {
  const [editing, setEditing] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [draft, setDraft] = useState(name);
  const [busy, setBusy] = useState(false);

  async function save(): Promise<void> {
    const trimmed = draft.trim();
    if (trimmed === "" || trimmed === name) {
      setEditing(false);
      setDraft(name);
      return;
    }
    setBusy(true);
    try {
      await onRename(trimmed);
      setEditing(false);
    } finally {
      setBusy(false);
    }
  }

  if (editing) {
    return (
      <div className="flex flex-1 items-center gap-2">
        <Input
          autoFocus
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") void save();
            if (event.key === "Escape") {
              setEditing(false);
              setDraft(name);
            }
          }}
          className="h-9"
        />
        <IconButton label="שמירה" onClick={() => void save()} disabled={busy}>
          <Check className="h-4 w-4 text-accent-600" />
        </IconButton>
        <IconButton
          label="ביטול"
          onClick={() => {
            setEditing(false);
            setDraft(name);
          }}
        >
          <X className="h-4 w-4" />
        </IconButton>
      </div>
    );
  }

  return (
    <div className="flex flex-1 items-center justify-between gap-2">
      <span className={className}>{name}</span>
      {confirming ? (
        <div className="flex items-center gap-2">
          <span className="text-xs text-ink-muted">{confirmLabel}</span>
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="text-rating-red"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await onDeactivate();
              } finally {
                setBusy(false);
                setConfirming(false);
              }
            }}
          >
            השבתה
          </Button>
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => setConfirming(false)}
          >
            ביטול
          </Button>
        </div>
      ) : (
        <div className="flex items-center gap-1">
          <IconButton label="עריכה" onClick={() => setEditing(true)}>
            <Pencil className="h-4 w-4" />
          </IconButton>
          <IconButton label="השבתה" onClick={() => setConfirming(true)}>
            <Trash2 className="h-4 w-4 text-rating-red" />
          </IconButton>
        </div>
      )}
    </div>
  );
}

function IconButton({
  label,
  onClick,
  disabled,
  children,
}: {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  children: ReactNode;
}): ReactNode {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      disabled={disabled}
      className="rounded p-1 text-ink-muted hover:bg-slate-100 hover:text-ink disabled:opacity-50"
    >
      {children}
    </button>
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
        onKeyDown={(event) => {
          if (event.key === "Enter" && value.trim() !== "" && !mutation.isPending) {
            mutation.mutate();
          }
        }}
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
