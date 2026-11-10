import { useState, type ReactNode } from "react";
import type { MedicalSummaryFields } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import { toggled } from "@/lib/utils/arrays";
import {
  OPTIONS,
  SECTIONS,
  maxLength,
  type LayoutItem,
} from "@/pages/student/medical/medicalSummaryLayout";

type Update = <K extends keyof MedicalSummaryFields>(
  key: K,
  value: MedicalSummaryFields[K]
) => void;

const YES_NO: { value: boolean; label: string }[] = [
  { value: true, label: "כן" },
  { value: false, label: "לא" },
];

export function MedicalSummaryForm({
  initial,
  initialDate,
  identity,
  pending,
  error,
  onSubmit,
  onCancel,
}: {
  initial: MedicalSummaryFields;
  initialDate?: string;
  identity: ReactNode;
  pending: boolean;
  error: unknown;
  onSubmit: (fields: MedicalSummaryFields, summaryDate: string) => void;
  onCancel: () => void;
}): ReactNode {
  const [draft, setDraft] = useState<MedicalSummaryFields>(initial);
  const [summaryDate, setSummaryDate] = useState(initialDate ?? "");
  const update: Update = (key, value) => setDraft((prev) => ({ ...prev, [key]: value }));
  const missingDate = initialDate !== undefined && !summaryDate;

  return (
    <div className="space-y-4">
      {error !== null && error !== undefined && (
        <Alert tone="error">{errorMessage(error)}</Alert>
      )}
      {identity}
      {initialDate !== undefined && (
        <div className="space-y-1.5">
          <Label htmlFor="ms-summary-date">תאריך הסיכום</Label>
          <Input
            id="ms-summary-date"
            type="date"
            className="w-48"
            value={summaryDate}
            onChange={(event) => setSummaryDate(event.target.value)}
          />
        </div>
      )}
      {SECTIONS.map((section) => (
        <Card key={section.title}>
          <CardHeader>
            <CardTitle>{section.title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {section.items.map((item) => (
              <FormItem key={item.key} item={item} draft={draft} update={update} />
            ))}
            {section.note && <p className="text-sm text-ink-muted">{section.note}</p>}
          </CardContent>
        </Card>
      ))}
      <div className="flex justify-start gap-2">
        <Button
          onClick={() => onSubmit(draft, summaryDate)}
          disabled={pending || missingDate}
        >
          {pending ? "שומר…" : "שמירה"}
        </Button>
        <Button variant="outline" onClick={onCancel} disabled={pending}>
          ביטול
        </Button>
      </div>
    </div>
  );
}

function FormItem({
  item,
  draft,
  update,
}: {
  item: LayoutItem;
  draft: MedicalSummaryFields;
  update: Update;
}): ReactNode {
  const id = `ms-${item.key}`;
  switch (item.kind) {
    case "text":
      return (
        <div className="space-y-1.5">
          <Label htmlFor={id}>{item.label}</Label>
          {item.multiline ? (
            <Textarea
              id={id}
              value={draft[item.key]}
              maxLength={maxLength(item)}
              onChange={(event) => update(item.key, event.target.value)}
              className="min-h-20"
            />
          ) : (
            <Input
              id={id}
              value={draft[item.key]}
              maxLength={maxLength(item)}
              onChange={(event) => update(item.key, event.target.value)}
            />
          )}
        </div>
      );
    case "date":
      return (
        <div className="space-y-1.5">
          <Label htmlFor={id}>{item.label}</Label>
          <Input
            id={id}
            type="date"
            className="w-48"
            value={draft[item.key] ?? ""}
            onChange={(event) => update(item.key, event.target.value || null)}
          />
        </div>
      );
    case "flag":
      return (
        <fieldset>
          <legend className="mb-2 text-sm font-medium text-ink">{item.label}</legend>
          <div className="flex flex-wrap gap-6">
            {YES_NO.map((option) => (
              <label
                key={option.label}
                className="flex items-center gap-2 text-sm text-ink"
              >
                <input
                  type="checkbox"
                  className="h-4 w-4"
                  checked={draft[item.key] === option.value}
                  onChange={(event) =>
                    update(item.key, event.target.checked ? option.value : null)
                  }
                />
                {option.label}
              </label>
            ))}
          </div>
        </fieldset>
      );
    case "options": {
      const chosen = draft[item.key];
      const other = item.other;
      return (
        <fieldset>
          <legend className="mb-2 text-sm font-medium text-ink">{item.label}</legend>
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            {OPTIONS[item.key].map((option) => (
              <label
                key={option.value}
                className="flex items-center gap-2 text-sm text-ink"
              >
                <input
                  type="checkbox"
                  className="h-4 w-4"
                  checked={chosen.includes(option.value)}
                  onChange={(event) => {
                    update(item.key, toggled(chosen, option.value, event.target.checked));
                    if (other && option.value === other.when && !event.target.checked) {
                      update(other.key, "");
                    }
                  }}
                />
                {option.label}
              </label>
            ))}
          </div>
          {other && chosen.includes(other.when) && (
            <Input
              aria-label={`${item.label} — פירוט`}
              placeholder="פירוט"
              className="mt-2"
              value={draft[other.key]}
              maxLength={300}
              onChange={(event) => update(other.key, event.target.value)}
            />
          )}
        </fieldset>
      );
    }
  }
}
