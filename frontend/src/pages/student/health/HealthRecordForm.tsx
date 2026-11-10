import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { healthRecordsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  HealthDomainInfo,
  HealthRecordRequest,
  HealthSessionType,
  StaffMember,
} from "@/lib/api/types";
import { StaffChipPicker } from "@/components/StaffChipPicker";
import { withAssigned } from "@/lib/utils/staff";
import { Textarea } from "@/components/ui/Textarea";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import { SESSION_TYPES, hasContent } from "@/pages/student/health/healthRecordFields";

const FIELD_CLASS =
  "h-11 w-full rounded-control border border-slate-300 bg-white px-2 text-sm text-ink shadow-soft focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-400/15";

export function HealthRecordForm({
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
  domains: HealthDomainInfo[];
  initial: HealthRecordRequest;
  assignedMembers?: StaffMember[];
  submitLabel: string;
  pending: boolean;
  error: unknown;
  onSubmit: (request: HealthRecordRequest) => void;
  onCancel: () => void;
}): ReactNode {
  const [draft, setDraft] = useState<HealthRecordRequest>(initial);
  const candidatesQuery = useQuery({
    queryKey: queryKeys.healthResponsibleCandidates(studentId),
    queryFn: () => healthRecordsApi.responsibleCandidates(studentId),
  });
  const candidates = withAssigned(candidatesQuery.data ?? [], assignedMembers);
  const selectable = domains.filter(
    (domain) => domain.is_active || domain.id === initial.domain_id
  );
  const update = (patch: Partial<HealthRecordRequest>): void =>
    setDraft((prev) => ({ ...prev, ...patch }));
  const canSubmit =
    !pending && draft.domain_id !== "" && draft.record_date !== "" && hasContent(draft);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div>
          <Label htmlFor="health-domain">תחום</Label>
          <select
            id="health-domain"
            value={draft.domain_id}
            onChange={(event) => update({ domain_id: event.target.value })}
            className={FIELD_CLASS}
          >
            <option value="">בחירה…</option>
            {selectable.map((domain) => (
              <option key={domain.id} value={domain.id}>
                {domain.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <Label htmlFor="health-date">תאריך</Label>
          <Input
            id="health-date"
            type="date"
            value={draft.record_date}
            onChange={(event) => update({ record_date: event.target.value })}
          />
        </div>
        <div>
          <Label htmlFor="health-session-type">אישי/קבוצתי</Label>
          <select
            id="health-session-type"
            value={draft.session_type ?? ""}
            onChange={(event) =>
              update({
                session_type:
                  event.target.value === ""
                    ? null
                    : (event.target.value as HealthSessionType),
              })
            }
            className={FIELD_CLASS}
          >
            <option value="">בחירה…</option>
            {SESSION_TYPES.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <TextField
        id="health-support"
        label="תמיכה שניתנה"
        value={draft.support_given}
        onChange={(value) => update({ support_given: value })}
      />

      <div>
        <Label>אחראי ביצוע</Label>
        {candidatesQuery.isError && (
          <Alert tone="error">
            לא ניתן לטעון את רשימת המשתמשים: {errorMessage(candidatesQuery.error)}
          </Alert>
        )}
        <div className="mt-1">
          <StaffChipPicker
            candidates={candidates}
            selected={draft.responsible_user_ids}
            onChange={(selected) => update({ responsible_user_ids: selected })}
          />
        </div>
      </div>

      <TextField
        id="health-notes"
        label="הערות"
        value={draft.notes}
        onChange={(value) => update({ notes: value })}
      />
      <TextField
        id="health-review"
        label="בקרת ביצוע"
        value={draft.execution_review}
        onChange={(value) => update({ execution_review: value })}
      />

      {error ? <Alert tone="error">{errorMessage(error)}</Alert> : null}
      <div className="flex justify-start gap-2">
        <Button onClick={() => onSubmit(draft)} disabled={!canSubmit}>
          {pending ? "שומר…" : submitLabel}
        </Button>
        <Button variant="ghost" onClick={onCancel}>
          ביטול
        </Button>
      </div>
    </div>
  );
}

function TextField({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
}): ReactNode {
  return (
    <div>
      <Label htmlFor={id}>{label}</Label>
      <Textarea
        id={id}
        value={value}
        maxLength={5000}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-20"
      />
    </div>
  );
}
