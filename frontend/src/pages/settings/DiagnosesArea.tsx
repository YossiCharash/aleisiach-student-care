import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, EyeOff } from "lucide-react";
import { diagnosesApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { DiagnosisCatalogResponse } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import {
  AddSettingInput,
  EditableSettingRow,
  SettingsListCard,
} from "@/pages/settings/SettingsList";

export function DiagnosesArea(): ReactNode {
  const [showInactive, setShowInactive] = useState(false);
  const query = useQuery({
    queryKey: [...queryKeys.diagnoses, showInactive],
    queryFn: () => diagnosesApi.list(showInactive),
  });
  const invalidate = useInvalidate();
  const create = useMutation({
    mutationFn: (name: string) => diagnosesApi.create(name),
    onSuccess: invalidate,
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

      <div className="max-w-2xl space-y-4">
        <AddSettingInput
          placeholder="שם אבחנה חדשה"
          buttonLabel="הוספת אבחנה"
          onSubmit={(name) => create.mutateAsync(name)}
        />

        {query.isLoading && <LoadingState />}
        {query.isError && <ErrorState error={query.error} />}
        {query.data &&
          (query.data.length === 0 ? (
            <EmptyState>אין אבחנות בקטלוג עדיין.</EmptyState>
          ) : (
            <SettingsListCard>
              {query.data.map((diagnosis) => (
                <DiagnosisRow key={diagnosis.id} diagnosis={diagnosis} />
              ))}
            </SettingsListCard>
          ))}
      </div>
    </div>
  );
}

function useInvalidate(): () => Promise<void> {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: queryKeys.diagnoses });
}

function DiagnosisRow({ diagnosis }: { diagnosis: DiagnosisCatalogResponse }): ReactNode {
  const invalidate = useInvalidate();
  const rename = useMutation({
    mutationFn: (name: string) => diagnosesApi.update(diagnosis.id, { name }),
    onSuccess: invalidate,
  });
  const setActive = useMutation({
    mutationFn: (isActive: boolean) =>
      diagnosesApi.update(diagnosis.id, { is_active: isActive }),
    onSuccess: invalidate,
  });

  return (
    <EditableSettingRow
      name={diagnosis.name}
      isActive={diagnosis.is_active}
      onRename={(name) => rename.mutateAsync(name)}
      onSetActive={(isActive) => setActive.mutateAsync(isActive)}
    />
  );
}
