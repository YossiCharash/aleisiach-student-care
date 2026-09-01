import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Eye, EyeOff, Pencil, Plus, RotateCcw, X } from "lucide-react";
import { diagnosesApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { DiagnosisCatalogResponse } from "@/lib/api/types";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";

export function DiagnosesArea(): ReactNode {
  const [showInactive, setShowInactive] = useState(false);
  const query = useQuery({
    queryKey: [...queryKeys.diagnoses, showInactive],
    queryFn: () => diagnosesApi.list(showInactive),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">אבחונים</h2>
          <p className="mt-1 text-sm text-ink-muted">
            קטלוג האבחנות המשותף. אבחנה חדשה שמוקלדת בפרטי תלמיד נוספת לכאן אוטומטית.
          </p>
        </div>
        <Button
          type="button"
          size="sm"
          variant={showInactive ? "secondary" : "outline"}
          onClick={() => setShowInactive((value) => !value)}
        >
          {showInactive ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          {showInactive ? "הסתר מושבתות" : "הצג מושבתות"}
        </Button>
      </div>

      <AddDiagnosis />

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data &&
        (query.data.length === 0 ? (
          <EmptyState>אין אבחנות בקטלוג עדיין.</EmptyState>
        ) : (
          <Card className="border-s-4 border-s-brand-300">
            <CardContent className="p-0">
              <ul>
                {query.data.map((diagnosis) => (
                  <DiagnosisRow key={diagnosis.id} diagnosis={diagnosis} />
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
    </div>
  );
}

function useInvalidate(): () => void {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.diagnoses });
  };
}

function AddDiagnosis(): ReactNode {
  const invalidate = useInvalidate();
  const [name, setName] = useState("");

  const mutation = useMutation({
    mutationFn: () => diagnosesApi.create(name.trim()),
    onSuccess: () => {
      invalidate();
      setName("");
    },
  });

  return (
    <div className="flex items-center gap-2">
      <Input
        value={name}
        placeholder="שם אבחנה חדשה"
        onChange={(event) => setName(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && name.trim() !== "" && !mutation.isPending) {
            mutation.mutate();
          }
        }}
        className="h-9 max-w-xs"
      />
      <Button
        type="button"
        size="sm"
        variant="outline"
        disabled={name.trim() === "" || mutation.isPending}
        onClick={() => mutation.mutate()}
      >
        <Plus className="h-4 w-4" />
        הוספת אבחנה
      </Button>
    </div>
  );
}

function DiagnosisRow({ diagnosis }: { diagnosis: DiagnosisCatalogResponse }): ReactNode {
  const invalidate = useInvalidate();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(diagnosis.name);

  const rename = useMutation({
    mutationFn: (name: string) => diagnosesApi.update(diagnosis.id, { name }),
    onSuccess: () => {
      invalidate();
      setEditing(false);
    },
  });
  const setActive = useMutation({
    mutationFn: (isActive: boolean) =>
      diagnosesApi.update(diagnosis.id, { is_active: isActive }),
    onSuccess: invalidate,
  });

  function save(): void {
    const trimmed = draft.trim();
    if (trimmed === "" || trimmed === diagnosis.name) {
      setEditing(false);
      setDraft(diagnosis.name);
      return;
    }
    rename.mutate(trimmed);
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
              if (event.key === "Enter") save();
              if (event.key === "Escape") {
                setEditing(false);
                setDraft(diagnosis.name);
              }
            }}
            className="h-9 max-w-xs"
          />
          <IconButton label="שמירה" onClick={save} disabled={rename.isPending}>
            <Check className="h-4 w-4 text-accent-600" />
          </IconButton>
          <IconButton
            label="ביטול"
            onClick={() => {
              setEditing(false);
              setDraft(diagnosis.name);
            }}
          >
            <X className="h-4 w-4" />
          </IconButton>
        </>
      ) : (
        <>
          <span
            className={`h-1.5 w-1.5 shrink-0 rounded-full ${diagnosis.is_active ? "bg-brand-400" : "bg-slate-300"}`}
            aria-hidden
          />
          <span
            className={`flex-1 text-sm font-medium ${diagnosis.is_active ? "text-ink" : "text-ink-muted line-through"}`}
          >
            {diagnosis.name}
          </span>
          {diagnosis.is_active ? (
            <>
              <IconButton label="עריכה" onClick={() => setEditing(true)}>
                <Pencil className="h-4 w-4" />
              </IconButton>
              <IconButton label="השבתה" onClick={() => setActive.mutate(false)}>
                <X className="h-4 w-4 text-rating-red" />
              </IconButton>
            </>
          ) : (
            <IconButton label="הפעלה מחדש" onClick={() => setActive.mutate(true)}>
              <RotateCcw className="h-4 w-4" />
            </IconButton>
          )}
        </>
      )}
    </li>
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
