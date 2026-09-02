import { useState, type ReactNode } from "react";
import { Check, Pencil, Plus, RotateCcw, X } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { errorMessage } from "@/components/ui/ErrorState";

export function SettingsIconButton({
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

export function SettingsListCard({ children }: { children: ReactNode }): ReactNode {
  return <ul className="flex flex-wrap items-start gap-2">{children}</ul>;
}

export function AddSettingInput({
  placeholder,
  buttonLabel,
  onSubmit,
}: {
  placeholder: string;
  buttonLabel: string;
  onSubmit: (value: string) => Promise<unknown>;
}): ReactNode {
  const [adding, setAdding] = useState(false);
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);

  function cancel(): void {
    setValue("");
    setAdding(false);
  }

  async function submit(): Promise<void> {
    const trimmed = value.trim();
    if (trimmed === "" || busy) {
      return;
    }
    setBusy(true);
    try {
      await onSubmit(trimmed);
      cancel();
    } finally {
      setBusy(false);
    }
  }

  if (!adding) {
    return (
      <Button type="button" size="sm" variant="outline" onClick={() => setAdding(true)}>
        <Plus className="h-4 w-4" />
        {buttonLabel}
      </Button>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <Input
        autoFocus
        value={value}
        placeholder={placeholder}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            void submit();
          }
          if (event.key === "Escape") {
            cancel();
          }
        }}
        className="h-9 max-w-xs"
      />
      <Button
        type="button"
        size="sm"
        disabled={value.trim() === "" || busy}
        onClick={() => void submit()}
      >
        {busy ? "שומר…" : "שמירה"}
      </Button>
      <Button type="button" size="sm" variant="ghost" onClick={cancel}>
        ביטול
      </Button>
    </div>
  );
}

export function EditableSettingRow({
  name,
  isActive = true,
  onRename,
  onSetActive,
}: {
  name: string;
  isActive?: boolean;
  onRename: (name: string) => Promise<unknown>;
  onSetActive?: (active: boolean) => Promise<unknown>;
}): ReactNode {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(name);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  function cancel(): void {
    setEditing(false);
    setDraft(name);
  }

  async function changeActive(active: boolean): Promise<void> {
    if (!onSetActive) {
      return;
    }
    setActionError(null);
    try {
      await onSetActive(active);
    } catch (caught) {
      setActionError(errorMessage(caught));
    }
  }

  async function save(): Promise<void> {
    const trimmed = draft.trim();
    if (trimmed === "" || trimmed === name) {
      cancel();
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

  return (
    <li className="flex flex-col gap-1 rounded-lg border border-slate-200 border-s-2 border-s-brand-300 bg-white py-1 pe-1 ps-2.5 shadow-sm">
      <div className="flex items-center gap-1.5">
        {editing ? (
          <>
            <Input
              autoFocus
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  void save();
                }
                if (event.key === "Escape") {
                  cancel();
                }
              }}
              className="h-8 w-40"
            />
            <SettingsIconButton label="שמירה" onClick={() => void save()} disabled={busy}>
              <Check className="h-4 w-4 text-accent-600" />
            </SettingsIconButton>
            <SettingsIconButton label="ביטול" onClick={cancel}>
              <X className="h-4 w-4" />
            </SettingsIconButton>
          </>
        ) : (
          <>
            <span
              className={`h-1.5 w-1.5 shrink-0 rounded-full ${isActive ? "bg-brand-400" : "bg-slate-300"}`}
              aria-hidden
            />
            <span
              className={`text-sm font-medium ${isActive ? "text-ink" : "text-ink-muted line-through"}`}
            >
              {name}
            </span>
            {isActive ? (
              <>
                <SettingsIconButton label="עריכה" onClick={() => setEditing(true)}>
                  <Pencil className="h-4 w-4" />
                </SettingsIconButton>
                {onSetActive && (
                  <SettingsIconButton
                    label="השבתה"
                    onClick={() => void changeActive(false)}
                  >
                    <X className="h-4 w-4 text-rating-red" />
                  </SettingsIconButton>
                )}
              </>
            ) : (
              onSetActive && (
                <SettingsIconButton
                  label="הפעלה מחדש"
                  onClick={() => void changeActive(true)}
                >
                  <RotateCcw className="h-4 w-4" />
                </SettingsIconButton>
              )
            )}
          </>
        )}
      </div>
      {actionError && (
        <p role="alert" className="max-w-xs pb-1 text-xs text-rating-red">
          {actionError}
        </p>
      )}
    </li>
  );
}
