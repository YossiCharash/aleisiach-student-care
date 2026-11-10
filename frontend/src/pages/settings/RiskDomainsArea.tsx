import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, EyeOff } from "lucide-react";
import { riskDomainsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { RiskCategory, RiskDomainInfo } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import {
  AddSettingInput,
  EditableSettingRow,
  SettingsListCard,
} from "@/pages/settings/SettingsList";

const CATEGORIES: { value: RiskCategory; label: string }[] = [
  { value: "medical", label: "רפואי" },
  { value: "behavioral", label: "התנהגותי" },
  { value: "independence", label: "עצמאות" },
];

export function RiskDomainsArea(): ReactNode {
  const [showInactive, setShowInactive] = useState(false);
  const query = useQuery({
    queryKey: [...queryKeys.riskDomains, showInactive],
    queryFn: () => riskDomainsApi.list(showInactive),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">תחומי סיכון</h2>
          <p className="mt-1 text-sm text-ink-muted">
            השורות שמופיעות בטבלת ניהול הסיכונים, לפי רפואי, התנהגותי ועצמאות. תחום מושבת
            לא יופיע בטבלאות חדשות, אבל יישאר בטבלאות שכבר מולאו בו.
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

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data &&
        CATEGORIES.map((category) => (
          <CategoryCard
            key={category.value}
            category={category.value}
            label={category.label}
            domains={query.data.filter((domain) => domain.category === category.value)}
          />
        ))}
    </div>
  );
}

function useInvalidate(): () => Promise<void> {
  const queryClient = useQueryClient();
  return () => queryClient.invalidateQueries({ queryKey: queryKeys.riskDomains });
}

function CategoryCard({
  category,
  label,
  domains,
}: {
  category: RiskCategory;
  label: string;
  domains: RiskDomainInfo[];
}): ReactNode {
  const invalidate = useInvalidate();
  const create = useMutation({
    mutationFn: (name: string) => riskDomainsApi.create(name, category),
    onSuccess: invalidate,
  });

  return (
    <section className="max-w-2xl space-y-4 rounded-card border border-s-4 border-slate-200 border-s-brand-400 bg-brand-50/40 p-4 shadow-sm">
      <h3 className="text-base font-semibold text-ink">{label}</h3>
      <AddSettingInput
        placeholder={`תחום סיכון חדש — ${label}`}
        buttonLabel="הוספת תחום"
        onSubmit={(name) => create.mutateAsync(name)}
      />
      {domains.length === 0 ? (
        <EmptyState>אין תחומי סיכון בקטגוריה זו.</EmptyState>
      ) : (
        <SettingsListCard>
          {domains.map((domain) => (
            <DomainRow key={domain.id} domain={domain} />
          ))}
        </SettingsListCard>
      )}
    </section>
  );
}

function DomainRow({ domain }: { domain: RiskDomainInfo }): ReactNode {
  const invalidate = useInvalidate();
  const rename = useMutation({
    mutationFn: (name: string) => riskDomainsApi.update(domain.id, { name }),
    onSuccess: invalidate,
  });
  const setActive = useMutation({
    mutationFn: (isActive: boolean) =>
      riskDomainsApi.update(domain.id, { is_active: isActive }),
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
