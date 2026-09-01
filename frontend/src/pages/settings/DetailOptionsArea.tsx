import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, EyeOff } from "lucide-react";
import { detailOptionsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { DetailOptionField, DetailOptionResponse } from "@/lib/api/types";
import { detailOptionFieldLabels } from "@/lib/utils/hebrew";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import {
  AddSettingInput,
  EditableSettingRow,
  SettingsListCard,
} from "@/pages/settings/SettingsList";

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

function useInvalidate(): () => Promise<void> {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: queryKeys.detailOptions });
}

function FieldGroup({
  field,
  options,
}: {
  field: DetailOptionField;
  options: DetailOptionResponse[];
}): ReactNode {
  const invalidate = useInvalidate();
  const create = useMutation({
    mutationFn: (name: string) => detailOptionsApi.create(field, name),
    onSuccess: invalidate,
  });

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-ink">{detailOptionFieldLabels[field]}</h3>
      <AddSettingInput
        placeholder="אפשרות חדשה"
        buttonLabel="הוספה"
        onSubmit={(name) => create.mutateAsync(name)}
      />
      {options.length === 0 ? (
        <EmptyState>אין אפשרויות.</EmptyState>
      ) : (
        <SettingsListCard>
          {options.map((option) => (
            <OptionRow key={option.id} option={option} />
          ))}
        </SettingsListCard>
      )}
    </div>
  );
}

function OptionRow({ option }: { option: DetailOptionResponse }): ReactNode {
  const invalidate = useInvalidate();
  const rename = useMutation({
    mutationFn: (name: string) => detailOptionsApi.update(option.id, { name }),
    onSuccess: invalidate,
  });
  const setActive = useMutation({
    mutationFn: (isActive: boolean) =>
      detailOptionsApi.update(option.id, { is_active: isActive }),
    onSuccess: invalidate,
  });

  return (
    <EditableSettingRow
      name={option.name}
      isActive={option.is_active}
      onRename={(name) => rename.mutateAsync(name)}
      onSetActive={(isActive) => setActive.mutateAsync(isActive)}
    />
  );
}
