import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Pencil, Plus, X } from "lucide-react";
import { classesApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ClassResponse } from "@/lib/api/types";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";

export function ClassesArea(): ReactNode {
  const query = useQuery({ queryKey: queryKeys.classes, queryFn: classesApi.list });

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-ink">כיתות</h2>
        <p className="mt-1 text-sm text-ink-muted">
          ניהול הכיתות שאליהן משויכים תלמידים ומדריכים.
        </p>
      </div>

      <AddClass />

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data &&
        (query.data.length === 0 ? (
          <EmptyState>אין כיתות עדיין.</EmptyState>
        ) : (
          <Card>
            <CardContent className="p-0">
              <ul>
                {query.data.map((classItem) => (
                  <ClassRow key={classItem.id} classItem={classItem} />
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
    </div>
  );
}

function AddClass(): ReactNode {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");

  const mutation = useMutation({
    mutationFn: () => classesApi.create(name.trim()),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.classes });
      setName("");
    },
  });

  return (
    <div className="flex items-center gap-2">
      <Input
        value={name}
        placeholder="שם כיתה חדשה"
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
        הוספת כיתה
      </Button>
    </div>
  );
}

function ClassRow({ classItem }: { classItem: ClassResponse }): ReactNode {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(classItem.name);

  const mutation = useMutation({
    mutationFn: (name: string) => classesApi.rename(classItem.id, name),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.classes });
      setEditing(false);
    },
  });

  function save(): void {
    const trimmed = draft.trim();
    if (trimmed === "" || trimmed === classItem.name) {
      setEditing(false);
      setDraft(classItem.name);
      return;
    }
    mutation.mutate(trimmed);
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
                setDraft(classItem.name);
              }
            }}
            className="h-9"
          />
          <IconButton label="שמירה" onClick={save} disabled={mutation.isPending}>
            <Check className="h-4 w-4 text-accent-600" />
          </IconButton>
          <IconButton
            label="ביטול"
            onClick={() => {
              setEditing(false);
              setDraft(classItem.name);
            }}
          >
            <X className="h-4 w-4" />
          </IconButton>
        </>
      ) : (
        <>
          <span className="flex-1 font-medium text-ink">{classItem.name}</span>
          <IconButton label="עריכה" onClick={() => setEditing(true)}>
            <Pencil className="h-4 w-4" />
          </IconButton>
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
