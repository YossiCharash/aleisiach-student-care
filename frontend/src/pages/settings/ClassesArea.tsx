import { type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { classesApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ClassResponse } from "@/lib/api/types";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import {
  AddSettingInput,
  EditableSettingRow,
  SettingsListCard,
} from "@/pages/settings/SettingsList";

export function ClassesArea(): ReactNode {
  const query = useQuery({ queryKey: queryKeys.classes, queryFn: classesApi.list });
  const invalidate = useInvalidate();
  const create = useMutation({
    mutationFn: (name: string) => classesApi.create(name),
    onSuccess: invalidate,
  });

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-ink">כיתות</h2>
        <p className="mt-1 text-sm text-ink-muted">
          ניהול הכיתות שאליהן משויכים תלמידים ומדריכים.
        </p>
      </div>

      <div className="max-w-2xl space-y-4 rounded-card border border-s-4 border-slate-200 border-s-brand-400 bg-brand-50/40 p-4 shadow-sm">
        <AddSettingInput
          placeholder="שם כיתה חדשה"
          buttonLabel="הוספת כיתה"
          onSubmit={(name) => create.mutateAsync(name)}
        />

        {query.isLoading && <LoadingState />}
        {query.isError && <ErrorState error={query.error} />}
        {query.data &&
          (query.data.length === 0 ? (
            <EmptyState>אין כיתות עדיין.</EmptyState>
          ) : (
            <SettingsListCard>
              {query.data.map((classItem) => (
                <ClassRow key={classItem.id} classItem={classItem} />
              ))}
            </SettingsListCard>
          ))}
      </div>
    </div>
  );
}

function useInvalidate(): () => Promise<void> {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: queryKeys.classes });
}

function ClassRow({ classItem }: { classItem: ClassResponse }): ReactNode {
  const invalidate = useInvalidate();
  const rename = useMutation({
    mutationFn: (name: string) => classesApi.rename(classItem.id, name),
    onSuccess: invalidate,
  });

  return (
    <EditableSettingRow
      name={classItem.name}
      onRename={(name) => rename.mutateAsync(name)}
    />
  );
}
