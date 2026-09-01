import { useState, type ReactNode } from "react";
import { Check, Pencil, Plus, RotateCcw, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

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
  return (
    <Card className="border-s-4 border-s-brand-300">
      <CardContent className="p-0">
        <ul>{children}</ul>
      </CardContent>
    </Card>
  );
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
  const [value, setValue] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(): Promise<void> {
    const trimmed = value.trim();
    if (trimmed === "" || busy) {
      return;
    }
    setBusy(true);
    try {
      await onSubmit(trimmed);
      setValue("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <Input
        value={value}
        placeholder={placeholder}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            void submit();
          }
        }}
        className="h-9 max-w-xs"
      />
      <Button
        type="button"
        size="sm"
        variant="outline"
        disabled={value.trim() === "" || busy}
        onClick={() => void submit()}
      >
        <Plus className="h-4 w-4" />
        {buttonLabel}
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

  function cancel(): void {
    setEditing(false);
    setDraft(name);
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
    <li className="flex items-center gap-2 border-b border-slate-100 px-3 py-2 last:border-0">
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
            className="h-9 max-w-xs"
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
            className={`flex-1 text-sm font-medium ${isActive ? "text-ink" : "text-ink-muted line-through"}`}
          >
            {name}
          </span>
          {isActive ? (
            <>
              <SettingsIconButton label="עריכה" onClick={() => setEditing(true)}>
                <Pencil className="h-4 w-4" />
              </SettingsIconButton>
              {onSetActive && (
                <SettingsIconButton label="השבתה" onClick={() => void onSetActive(false)}>
                  <X className="h-4 w-4 text-rating-red" />
                </SettingsIconButton>
              )}
            </>
          ) : (
            onSetActive && (
              <SettingsIconButton
                label="הפעלה מחדש"
                onClick={() => void onSetActive(true)}
              >
                <RotateCcw className="h-4 w-4" />
              </SettingsIconButton>
            )
          )}
        </>
      )}
    </li>
  );
}
