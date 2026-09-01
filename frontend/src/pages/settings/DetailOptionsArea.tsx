import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Eye, EyeOff, Pencil, Plus, RotateCcw, X } from "lucide-react";
import { detailOptionsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { DetailOptionField, DetailOptionResponse } from "@/lib/api/types";
import { detailOptionFieldLabels } from "@/lib/utils/hebrew";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";

const FIELD_ORDER = Object.keys(detailOptionFieldLabels) as DetailOptionField[];

export function DetailOptionsArea(): ReactNode {
  const [showInactive, setShowInactive] = useState(false);
  const query = useQuery({
    queryKey: [...queryKeys.detailOptions, showInactive],
    queryFn: () => detailOptionsApi.list(showInactive),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">עריכת פרטי תלמיד</h2>
          <p className="mt-1 text-sm text-ink-muted">
            ניהול האפשרויות של רשימות הבחירה בפרטי תלמיד. שינויים משתקפים מיד בטופס.
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

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data &&
        FIELD_ORDER.map((field) => (
          <FieldGroup
            key={field}
            field={field}
            options={query.data.filter((option) => option.field === field)}
          />
        ))}
    </div>
  );
}

function useInvalidate(): () => void {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.detailOptions });
  };
}

function FieldGroup({
  field,
  options,
}: {
  field: DetailOptionField;
  options: DetailOptionResponse[];
}): ReactNode {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-ink">{detailOptionFieldLabels[field]}</h3>
      <AddOption field={field} />
      {options.length === 0 ? (
        <EmptyState>אין אפשרויות.</EmptyState>
      ) : (
        <Card>
          <CardContent className="p-0">
            <ul>
              {options.map((option) => (
                <OptionRow key={option.id} option={option} />
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function AddOption({ field }: { field: DetailOptionField }): ReactNode {
  const invalidate = useInvalidate();
  const [name, setName] = useState("");

  const mutation = useMutation({
    mutationFn: () => detailOptionsApi.create(field, name.trim()),
    onSuccess: () => {
      invalidate();
      setName("");
    },
  });

  return (
    <div className="flex items-center gap-2">
      <Input
        value={name}
        placeholder="אפשרות חדשה"
        onChange={(event) => setName(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && name.trim() !== "" && !mutation.isPending) {
            mutation.mutate();
          }
        }}
        className="h-9"
      />
      <Button
        type="button"
        size="sm"
        variant="outline"
        disabled={name.trim() === "" || mutation.isPending}
        onClick={() => mutation.mutate()}
      >
        <Plus className="h-4 w-4" />
        הוספה
      </Button>
    </div>
  );
}

function OptionRow({ option }: { option: DetailOptionResponse }): ReactNode {
  const invalidate = useInvalidate();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(option.name);

  const rename = useMutation({
    mutationFn: (name: string) => detailOptionsApi.update(option.id, { name }),
    onSuccess: () => {
      invalidate();
      setEditing(false);
    },
  });
  const setActive = useMutation({
    mutationFn: (isActive: boolean) =>
      detailOptionsApi.update(option.id, { is_active: isActive }),
    onSuccess: invalidate,
  });

  function save(): void {
    const trimmed = draft.trim();
    if (trimmed === "" || trimmed === option.name) {
      setEditing(false);
      setDraft(option.name);
      return;
    }
    rename.mutate(trimmed);
  }

  return (
    <li className="flex items-center gap-2 border-b border-slate-50 px-4 py-3 last:border-0">
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
                setDraft(option.name);
              }
            }}
            className="h-9"
          />
          <IconButton label="שמירה" onClick={save} disabled={rename.isPending}>
            <Check className="h-4 w-4 text-accent-600" />
          </IconButton>
          <IconButton
            label="ביטול"
            onClick={() => {
              setEditing(false);
              setDraft(option.name);
            }}
          >
            <X className="h-4 w-4" />
          </IconButton>
        </>
      ) : (
        <>
          <span
            className={`flex-1 font-medium ${option.is_active ? "text-ink" : "text-ink-muted line-through"}`}
          >
            {option.name}
          </span>
          {option.is_active ? (
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
