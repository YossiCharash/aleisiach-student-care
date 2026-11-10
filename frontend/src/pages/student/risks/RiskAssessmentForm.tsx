import { Fragment, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { riskAssessmentApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  RiskAssessmentRequest,
  RiskDomainInfo,
  RiskItemFields,
  RiskLevel,
  StaffMember,
} from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";
import { toggled } from "@/lib/utils/arrays";
import { Textarea } from "@/components/ui/Textarea";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import {
  COLUMN_TITLES,
  RISK_LEVELS,
  groupByCategory,
} from "@/pages/student/risks/riskLevels";

type UpdateItem = (domain: string, patch: Partial<RiskItemFields>) => void;

export function RiskAssessmentForm({
  studentId,
  domains,
  initial,
  assignedMembers = [],
  submitLabel,
  pending,
  error,
  onSubmit,
  onCancel,
}: {
  studentId: string;
  domains: RiskDomainInfo[];
  initial: RiskAssessmentRequest;
  assignedMembers?: StaffMember[];
  submitLabel: string;
  pending: boolean;
  error: unknown;
  onSubmit: (request: RiskAssessmentRequest) => void;
  onCancel: () => void;
}): ReactNode {
  const [draft, setDraft] = useState<RiskAssessmentRequest>(initial);
  const candidatesQuery = useQuery({
    queryKey: queryKeys.riskResponsibleCandidates(studentId),
    queryFn: () => riskAssessmentApi.responsibleCandidates(studentId),
  });
  const candidates = withAssigned(candidatesQuery.data ?? [], assignedMembers);
  const byDomain = new Map(draft.items.map((item) => [item.domain_id, item]));

  const updateItem: UpdateItem = (domain, patch) =>
    setDraft((prev) => ({
      ...prev,
      items: prev.items.map((item) =>
        item.domain_id === domain ? { ...item, ...patch } : item
      ),
    }));

  return (
    <div className="space-y-4">
      <div className="w-48">
        <Label htmlFor="risk-date">תאריך</Label>
        <Input
          id="risk-date"
          type="date"
          value={draft.assessment_date}
          onChange={(event) =>
            setDraft((prev) => ({ ...prev, assessment_date: event.target.value }))
          }
        />
      </div>

      {candidatesQuery.isError && (
        <Alert tone="error">
          לא ניתן לטעון את רשימת המשתמשים לבחירת אחראי ביצוע:{" "}
          {errorMessage(candidatesQuery.error)}
        </Alert>
      )}

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-brand-600 text-white">
              {COLUMN_TITLES.map((title) => (
                <th key={title} className="p-2 text-start font-medium">
                  {title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {groupByCategory(domains.filter((domain) => byDomain.has(domain.id))).map(
              (group) => (
                <Fragment key={group.category}>
                  <tr className="bg-brand-50">
                    <td
                      colSpan={COLUMN_TITLES.length}
                      className="p-2 font-semibold text-brand-700"
                    >
                      {group.label}
                    </td>
                  </tr>
                  {group.domains.map((domain) => {
                    const item = byDomain.get(domain.id);
                    return item ? (
                      <RiskRow
                        key={domain.id}
                        domain={domain}
                        item={item}
                        candidates={candidates}
                        updateItem={updateItem}
                      />
                    ) : null;
                  })}
                </Fragment>
              )
            )}
          </tbody>
        </table>
      </div>

      {error ? <Alert tone="error">{errorMessage(error)}</Alert> : null}
      <div className="flex justify-start gap-2">
        <Button
          onClick={() => onSubmit(draft)}
          disabled={pending || draft.assessment_date === ""}
        >
          {pending ? "שומר…" : submitLabel}
        </Button>
        <Button variant="ghost" onClick={onCancel}>
          ביטול
        </Button>
      </div>
    </div>
  );
}

function withAssigned(candidates: StaffMember[], assigned: StaffMember[]): StaffMember[] {
  const known = new Set(candidates.map((member) => member.id));
  const missing = assigned.filter(
    (member, index) =>
      !known.has(member.id) &&
      assigned.findIndex((other) => other.id === member.id) === index
  );
  return [...candidates, ...missing];
}

function RiskRow({
  domain,
  item,
  candidates,
  updateItem,
}: {
  domain: RiskDomainInfo;
  item: RiskItemFields;
  candidates: StaffMember[];
  updateItem: UpdateItem;
}): ReactNode {
  const id = `risk-${domain.id}`;

  return (
    <tr className="border-b border-slate-200 align-top">
      <td className="w-1/6 p-2 font-medium text-ink">{domain.name}</td>
      <td className="p-2">
        <Textarea
          aria-label={`מהות הסיכון — ${domain.name}`}
          value={item.nature}
          maxLength={2000}
          onChange={(event) => updateItem(domain.id, { nature: event.target.value })}
          className="min-h-20"
        />
      </td>
      <td className="w-32 p-2">
        <select
          id={`${id}-level`}
          aria-label={`רמת סיכון — ${domain.name}`}
          value={item.level ?? ""}
          onChange={(event) =>
            updateItem(domain.id, {
              level: event.target.value === "" ? null : (event.target.value as RiskLevel),
            })
          }
          className="h-11 w-full rounded-control border border-slate-300 bg-white px-2 text-sm text-ink shadow-soft focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-400/15"
        >
          <option value="">בחירה…</option>
          {RISK_LEVELS.map((level) => (
            <option key={level.value} value={level.value}>
              {level.label}
            </option>
          ))}
        </select>
      </td>
      <td className="p-2">
        <Textarea
          aria-label={`תוכנית התערבות — ${domain.name}`}
          value={item.intervention_plan}
          maxLength={5000}
          onChange={(event) =>
            updateItem(domain.id, { intervention_plan: event.target.value })
          }
          className="min-h-20"
        />
      </td>
      <td className="w-48 p-2">
        <div className="flex flex-wrap gap-1.5">
          {candidates.map((member) => {
            const selected = item.responsible_user_ids.includes(member.id);
            return (
              <button
                key={member.id}
                type="button"
                aria-pressed={selected}
                aria-label={`${member.full_name} — אחראי ביצוע ל${domain.name}`}
                onClick={() =>
                  updateItem(domain.id, {
                    responsible_user_ids: toggled(
                      item.responsible_user_ids,
                      member.id,
                      !selected
                    ),
                  })
                }
                className={cn(
                  "rounded-full border px-2.5 py-0.5 text-xs transition-colors",
                  selected
                    ? "border-brand-500 bg-brand-500 text-white"
                    : "border-slate-200 bg-white text-ink-muted hover:border-brand-300 hover:text-ink"
                )}
              >
                {member.full_name}
              </button>
            );
          })}
        </div>
      </td>
    </tr>
  );
}
