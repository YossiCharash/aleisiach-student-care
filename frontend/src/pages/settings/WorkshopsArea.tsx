import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Eye, EyeOff, Pencil, Plus, RotateCcw } from "lucide-react";
import { workshopsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { WorkshopResponse } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { SettingsListCard } from "@/pages/settings/SettingsList";
import { WorkshopDialog } from "@/pages/settings/WorkshopDialog";

export function WorkshopsArea(): ReactNode {
  const [showArchived, setShowArchived] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<WorkshopResponse | undefined>(undefined);

  const activeQuery = useQuery({
    queryKey: queryKeys.workshops,
    queryFn: workshopsApi.list,
  });
  const archivedQuery = useQuery({
    queryKey: [...queryKeys.workshops, "archived"],
    queryFn: workshopsApi.listArchived,
    enabled: showArchived,
  });

  function openCreate(): void {
    setEditing(undefined);
    setDialogOpen(true);
  }

  function openEdit(workshop: WorkshopResponse): void {
    setEditing(workshop);
    setDialogOpen(true);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">סדנאות</h2>
          <p className="mt-1 text-sm text-ink-muted">
            ניהול הסדנאות במוסד — שם, צבע מזהה ומדריך אחראי. תלמידים משויכים לסדנה בכרטיס
            התלמיד.
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            type="button"
            size="sm"
            variant={showArchived ? "secondary" : "outline"}
            onClick={() => setShowArchived((value) => !value)}
          >
            {showArchived ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            {showArchived ? "הסתר ארכיון" : "הצג ארכיון"}
          </Button>
          <Button type="button" size="sm" onClick={openCreate}>
            <Plus className="h-4 w-4" />
            סדנה חדשה
          </Button>
        </div>
      </div>

      <div className="max-w-2xl space-y-4">
        {activeQuery.isLoading && <LoadingState />}
        {activeQuery.isError && <ErrorState error={activeQuery.error} />}
        {activeQuery.data &&
          (activeQuery.data.length === 0 ? (
            <EmptyState>אין סדנאות עדיין.</EmptyState>
          ) : (
            <SettingsListCard>
              {activeQuery.data.map((workshop) => (
                <WorkshopRow
                  key={workshop.id}
                  workshop={workshop}
                  onEdit={() => openEdit(workshop)}
                />
              ))}
            </SettingsListCard>
          ))}

        {showArchived && (
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-ink-muted">ארכיון</h3>
            {archivedQuery.isLoading && <LoadingState />}
            {archivedQuery.isError && <ErrorState error={archivedQuery.error} />}
            {archivedQuery.data &&
              (archivedQuery.data.length === 0 ? (
                <EmptyState>אין סדנאות בארכיון.</EmptyState>
              ) : (
                <SettingsListCard>
                  {archivedQuery.data.map((workshop) => (
                    <ArchivedWorkshopRow key={workshop.id} workshop={workshop} />
                  ))}
                </SettingsListCard>
              ))}
          </div>
        )}
      </div>

      <WorkshopDialog open={dialogOpen} onOpenChange={setDialogOpen} workshop={editing} />
    </div>
  );
}

function useInvalidate(): () => Promise<void> {
  const queryClient = useQueryClient();
  return async () => {
    await queryClient.invalidateQueries({ queryKey: queryKeys.workshops });
  };
}

function WorkshopRow({
  workshop,
  onEdit,
}: {
  workshop: WorkshopResponse;
  onEdit: () => void;
}): ReactNode {
  const invalidate = useInvalidate();
  const archive = useMutation({
    mutationFn: () => workshopsApi.archive(workshop.id),
    onSuccess: invalidate,
  });

  return (
    <div className="flex items-center gap-3 px-3 py-2">
      <span
        className="inline-block h-4 w-4 shrink-0 rounded-full border border-slate-300"
        style={{ backgroundColor: workshop.color }}
        aria-hidden
      />
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-ink">{workshop.name}</p>
        <p className="truncate text-xs text-ink-muted">
          {workshop.instructor_name ?? "ללא מדריך"}
        </p>
      </div>
      {archive.isError && (
        <span className="text-xs text-rating-red">לא ניתן להעביר לארכיון</span>
      )}
      <Button type="button" size="sm" variant="ghost" onClick={onEdit} aria-label="עריכה">
        <Pencil className="h-4 w-4" />
      </Button>
      <Button
        type="button"
        size="sm"
        variant="ghost"
        onClick={() => archive.mutate()}
        disabled={archive.isPending}
        aria-label="העברה לארכיון"
      >
        <Archive className="h-4 w-4" />
      </Button>
    </div>
  );
}

function ArchivedWorkshopRow({ workshop }: { workshop: WorkshopResponse }): ReactNode {
  const invalidate = useInvalidate();
  const restore = useMutation({
    mutationFn: () => workshopsApi.restore(workshop.id),
    onSuccess: invalidate,
  });

  return (
    <div className="flex items-center gap-3 px-3 py-2">
      <span
        className="inline-block h-4 w-4 shrink-0 rounded-full border border-slate-300"
        style={{ backgroundColor: workshop.color }}
        aria-hidden
      />
      <p className="min-w-0 flex-1 truncate font-medium text-ink-muted">
        {workshop.name}
      </p>
      <Button
        type="button"
        size="sm"
        variant="ghost"
        onClick={() => restore.mutate()}
        disabled={restore.isPending}
      >
        <RotateCcw className="h-4 w-4" />
        שחזור
      </Button>
    </div>
  );
}
