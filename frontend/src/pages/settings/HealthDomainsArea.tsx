import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, EyeOff } from "lucide-react";
import { healthDomainsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { HealthDomainInfo } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import {
  AddSettingInput,
  EditableSettingRow,
  SettingsListCard,
} from "@/pages/settings/SettingsList";

export function HealthDomainsArea(): ReactNode {
  const [showInactive, setShowInactive] = useState(false);
  const invalidate = useInvalidate();
  const query = useQuery({
    queryKey: [...queryKeys.healthDomains, showInactive],
    queryFn: () => healthDomainsApi.list(showInactive),
  });
  const create = useMutation({
    mutationFn: (name: string) => healthDomainsApi.create(name),
    onSuccess: invalidate,
  });

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">תחומי מקצועות הבריאות</h2>
          <p className="mt-1 text-sm text-ink-muted">
            התחומים שמהם בוחרים בטבלת התיעוד האישי של מקצועות הבריאות (למשל פיזיותרפיה).
            תחום מושבת לא יוצע בשורות חדשות, אבל יישאר בשורות שכבר תועדו בו.
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

      <section className="max-w-2xl space-y-4 rounded-card border border-s-4 border-slate-200 border-s-brand-400 bg-brand-50/40 p-4 shadow-sm">
        <AddSettingInput
          placeholder="תחום חדש"
          buttonLabel="הוספת תחום"
          onSubmit={(name) => create.mutateAsync(name)}
        />
        {query.isLoading && <LoadingState />}
        {query.isError && <ErrorState error={query.error} />}
        {query.data &&
          (query.data.length === 0 ? (
            <EmptyState>עדיין לא הוגדרו תחומים.</EmptyState>
          ) : (
            <SettingsListCard>
              {query.data.map((domain) => (
                <DomainRow key={domain.id} domain={domain} />
              ))}
            </SettingsListCard>
          ))}
      </section>
    </div>
  );
}

function useInvalidate(): () => Promise<void> {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: queryKeys.healthDomains });
}

function DomainRow({ domain }: { domain: HealthDomainInfo }): ReactNode {
  const invalidate = useInvalidate();
  const rename = useMutation({
    mutationFn: (name: string) => healthDomainsApi.update(domain.id, { name }),
    onSuccess: invalidate,
  });
  const setActive = useMutation({
    mutationFn: (isActive: boolean) =>
      healthDomainsApi.update(domain.id, { is_active: isActive }),
    onSuccess: invalidate,
  });

  return (
    <EditableSettingRow
      name={domain.name}
      isActive={domain.is_active}
      onRename={(name) => rename.mutateAsync(name)}
      onSetActive={(isActive) => setActive.mutateAsync(isActive)}
    />
  );
}
