import {
  createContext,
  useContext,
  useState,
  type KeyboardEvent,
  type ReactNode,
} from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, ChevronDown, Eye, EyeOff, Pencil, RotateCcw, X } from "lucide-react";
import { taxonomyApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { LabelTreeNode, SkillTreeNode, SubLabelTreeNode } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { AddSettingInput, SettingsIconButton } from "@/pages/settings/SettingsList";

const ShowInactiveContext = createContext(false);

function useTreeMutation<TArgs>(
  mutationFn: (args: TArgs) => Promise<unknown>
): (args: TArgs) => Promise<unknown> {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["taxonomy"] });
    },
  });
  return mutation.mutateAsync;
}

export function TaxonomyArea(): ReactNode {
  const query = useQuery({ queryKey: queryKeys.taxonomyTree, queryFn: taxonomyApi.tree });
  const [showInactive, setShowInactive] = useState(false);
  const createLabel = useTreeMutation((name: string) => taxonomyApi.createLabel(name));

  return (
    <ShowInactiveContext.Provider value={showInactive}>
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-ink">כישורים</h2>
            <p className="mt-1 text-sm text-ink-muted">
              תוויות ← תת-תוויות ← כישורים ← פתרונות. שינויים משתקפים מיד בטופס הישיבות.
            </p>
          </div>
          <Button
            type="button"
            size="sm"
            variant={showInactive ? "secondary" : "outline"}
            onClick={() => setShowInactive((value) => !value)}
          >
            {showInactive ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            {showInactive ? "הסתר מושבתים" : "הצג מושבתים"}
          </Button>
        </div>

        <AddSettingInput
          placeholder="שם תווית חדשה"
          buttonLabel="הוספת תווית"
          onSubmit={createLabel}
        />

        {query.isLoading && <LoadingState />}
        {query.isError && <ErrorState error={query.error} />}
        {query.data &&
          (query.data.length === 0 ? (
            <EmptyState>אין תוויות עדיין.</EmptyState>
          ) : (
            <div className="grid grid-cols-2 items-start gap-3">
              {query.data.map((label, index) => (
                <LabelNode key={label.id} label={label} index={index + 1} />
              ))}
            </div>
          ))}

        <InactiveNodeList
          heading="תוויות מושבתות"
          emptyLabel="אין תוויות מושבתות."
          queryKey={queryKeys.taxonomyLabels}
          queryFn={() => taxonomyApi.listLabels(true)}
          getLabel={(label) => label.name}
          onReactivate={(id) => taxonomyApi.updateLabel(id, { is_active: true })}
        />
      </div>
    </ShowInactiveContext.Provider>
  );
}

function headerToggleProps(toggle: () => void): {
  role: "button";
  tabIndex: number;
  onClick: () => void;
  onKeyDown: (event: KeyboardEvent<HTMLDivElement>) => void;
} {
  return {
    role: "button",
    tabIndex: 0,
    onClick: toggle,
    onKeyDown: (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
    },
  };
}

function Chip({ children }: { children: ReactNode }): ReactNode {
  return (
    <span className="whitespace-nowrap rounded-md bg-slate-100 px-2 py-0.5 text-xs text-ink-muted">
      {children}
    </span>
  );
}

function CollapseToggle({
  open,
  onClick,
}: {
  open: boolean;
  onClick: () => void;
}): ReactNode {
  return (
    <button
      type="button"
      onClick={(event) => {
        event.stopPropagation();
        onClick();
      }}
      className="text-ink-muted hover:text-ink"
      aria-label={open ? "כווץ" : "הרחב"}
      aria-expanded={open}
    >
      <ChevronDown
        className={`h-4 w-4 transition-transform ${open ? "" : "-rotate-90"}`}
      />
    </button>
  );
}

function LabelNode({ label, index }: { label: LabelTreeNode; index: number }): ReactNode {
  const [open, setOpen] = useState(false);
  const rename = useTreeMutation((name: string) =>
    taxonomyApi.updateLabel(label.id, { name })
  );
  const deactivate = useTreeMutation(() =>
    taxonomyApi.updateLabel(label.id, { is_active: false })
  );
  const createSubLabel = useTreeMutation((name: string) =>
    taxonomyApi.createSubLabel(label.id, name)
  );

  const skillCount = label.sub_labels.reduce(
    (total, subLabel) => total + subLabel.skills.length,
    0
  );

  return (
    <div className="overflow-hidden rounded-card border border-s-4 border-slate-200 border-s-brand-400 bg-white shadow-sm">
      <div
        className="flex cursor-pointer items-center gap-3 bg-brand-50/50 px-4 py-3"
        {...headerToggleProps(() => setOpen((value) => !value))}
      >
        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-brand-50 text-xs font-semibold text-brand-700">
          {index}
        </span>
        <NodeName
          name={label.name}
          className="text-base font-semibold text-ink"
          onRename={(name) => rename(name)}
          onDeactivate={() => deactivate(undefined)}
          confirmLabel="להשבית את התווית וכל תוכנה?"
          extra={
            <Chip>
              {label.sub_labels.length} תת-תוויות · {skillCount} כישורים
            </Chip>
          }
        />
        <CollapseToggle open={open} onClick={() => setOpen((value) => !value)} />
      </div>
      {open && (
        <div className="space-y-3 border-t border-slate-100 p-4">
          <AddSettingInput
            placeholder="שם תת-תווית"
            buttonLabel="הוספת תת-תווית"
            onSubmit={createSubLabel}
          />
          {label.sub_labels.map((subLabel) => (
            <SubLabelNode key={subLabel.id} subLabel={subLabel} />
          ))}
          <InactiveNodeList
            heading="תת-תוויות מושבתות"
            emptyLabel="אין תת-תוויות מושבתות."
            queryKey={queryKeys.taxonomySubLabels(label.id)}
            queryFn={() => taxonomyApi.listSubLabels(label.id, true)}
            getLabel={(subLabel) => subLabel.name}
            onReactivate={(id) => taxonomyApi.updateSubLabel(id, { is_active: true })}
          />
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
  const createSkill = useTreeMutation((name: string) =>
    taxonomyApi.createSkill(subLabel.id, name)
  );

  return (
    <div className="ms-4 rounded-lg border border-s-4 border-slate-200 border-s-brand-300 bg-white">
      <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50/50 px-3 py-2.5">
        <NodeName
          name={subLabel.name}
          className="text-sm font-semibold text-ink"
          onRename={(name) => rename(name)}
          onDeactivate={() => deactivate(undefined)}
          confirmLabel="להשבית את תת-התווית?"
          extra={<Chip>{subLabel.skills.length} כישורים</Chip>}
        />
      </div>
      <div className="space-y-2 p-3">
        <AddSettingInput
          placeholder="שם כישור"
          buttonLabel="הוספת כישור"
          onSubmit={createSkill}
        />
        {subLabel.skills.length > 0 && (
          <div className="ms-4 space-y-2">
            {subLabel.skills.map((skill) => (
              <SkillNode key={skill.id} skill={skill} />
            ))}
          </div>
        )}
        <InactiveNodeList
          heading="כישורים מושבתים"
          emptyLabel="אין כישורים מושבתים."
          queryKey={queryKeys.taxonomySkills(subLabel.id)}
          queryFn={() => taxonomyApi.listSkills(subLabel.id, true)}
          getLabel={(skill) => skill.name}
          onReactivate={(id) => taxonomyApi.updateSkill(id, { is_active: true })}
        />
      </div>
    </div>
  );
}

function SkillNode({ skill }: { skill: SkillTreeNode }): ReactNode {
  const [open, setOpen] = useState(false);
  const rename = useTreeMutation((name: string) =>
    taxonomyApi.updateSkill(skill.id, { name })
  );
  const deactivate = useTreeMutation(() =>
    taxonomyApi.updateSkill(skill.id, { is_active: false })
  );
  const createSolution = useTreeMutation((text: string) =>
    taxonomyApi.createSolution(skill.id, text)
  );

  return (
    <div className="rounded-lg border border-s-4 border-slate-200 border-s-brand-200 bg-white">
      <div
        className="flex cursor-pointer items-center gap-2 px-3 py-2"
        {...headerToggleProps(() => setOpen((value) => !value))}
      >
        <NodeName
          name={skill.name}
          className="text-sm font-medium text-ink"
          onRename={(name) => rename(name)}
          onDeactivate={() => deactivate(undefined)}
          confirmLabel="להשבית את הכישור?"
          extra={<Chip>{skill.solutions.length} פתרונות</Chip>}
        />
        <CollapseToggle open={open} onClick={() => setOpen((value) => !value)} />
      </div>
      {open && (
        <div className="space-y-2 border-t border-slate-100 p-3">
          <AddSettingInput
            placeholder="טקסט פתרון"
            buttonLabel="הוספת פתרון"
            onSubmit={createSolution}
          />
          {skill.solutions.length > 0 && (
            <ul className="space-y-1">
              {skill.solutions.map((solution) => (
                <SolutionRow key={solution.id} id={solution.id} text={solution.text} />
              ))}
            </ul>
          )}
          <InactiveNodeList
            heading="פתרונות מושבתים"
            emptyLabel="אין פתרונות מושבתים."
            queryKey={queryKeys.taxonomySolutions(skill.id)}
            queryFn={() => taxonomyApi.listSolutions(skill.id, true)}
            getLabel={(solution) => solution.text}
            onReactivate={(id) => taxonomyApi.updateSolution(id, { is_active: true })}
          />
        </div>
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
    <li className="ms-4 rounded-md bg-white px-3 py-1.5">
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

interface InactiveNode {
  id: string;
  is_active: boolean;
}

function InactiveNodeList<T extends InactiveNode>({
  heading,
  emptyLabel,
  queryKey,
  queryFn,
  getLabel,
  onReactivate,
}: {
  heading: string;
  emptyLabel: string;
  queryKey: readonly unknown[];
  queryFn: () => Promise<T[]>;
  getLabel: (item: T) => string;
  onReactivate: (id: string) => Promise<unknown>;
}): ReactNode {
  const showInactive = useContext(ShowInactiveContext);
  const [open, setOpen] = useState(false);
  const query = useQuery({ queryKey, queryFn, enabled: open && showInactive });
  const reactivate = useTreeMutation(onReactivate);

  const inactive = (query.data ?? []).filter((item) => !item.is_active);

  if (!showInactive) {
    return null;
  }

  return (
    <div className="border-t border-slate-100 pt-2">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex items-center gap-1.5 text-xs text-ink-muted hover:text-ink"
        aria-expanded={open}
      >
        <ChevronDown className={`h-3.5 w-3.5 ${open ? "" : "-rotate-90"}`} />
        {heading}
      </button>
      {open && (
        <div className="mt-2 space-y-2">
          {query.isLoading && <LoadingState />}
          {query.isError && <ErrorState error={query.error} />}
          {query.data &&
            (inactive.length === 0 ? (
              <EmptyState>{emptyLabel}</EmptyState>
            ) : (
              inactive.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2"
                >
                  <span className="text-sm text-ink-muted">{getLabel(item)}</span>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => void reactivate(item.id)}
                  >
                    <RotateCcw className="h-4 w-4" />
                    הפעלה מחדש
                  </Button>
                </div>
              ))
            ))}
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
  extra,
}: {
  name: string;
  className?: string;
  onRename: (name: string) => Promise<unknown>;
  onDeactivate: () => Promise<unknown>;
  confirmLabel: string;
  extra?: ReactNode;
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
      <div
        className="flex flex-1 items-center gap-2"
        onClick={(event) => event.stopPropagation()}
      >
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
        <SettingsIconButton label="שמירה" onClick={() => void save()} disabled={busy}>
          <Check className="h-4 w-4 text-accent-600" />
        </SettingsIconButton>
        <SettingsIconButton
          label="ביטול"
          onClick={() => {
            setEditing(false);
            setDraft(name);
          }}
        >
          <X className="h-4 w-4" />
        </SettingsIconButton>
      </div>
    );
  }

  return (
    <div className="flex flex-1 items-center gap-2">
      <span className={className}>{name}</span>
      {extra}
      <div
        className="flex flex-1 items-center justify-end gap-1"
        onClick={(event) => event.stopPropagation()}
      >
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
          <>
            <SettingsIconButton label="עריכה" onClick={() => setEditing(true)}>
              <Pencil className="h-4 w-4" />
            </SettingsIconButton>
            <SettingsIconButton label="השבתה" onClick={() => setConfirming(true)}>
              <X className="h-4 w-4 text-rating-red" />
            </SettingsIconButton>
          </>
        )}
      </div>
    </div>
  );
}
