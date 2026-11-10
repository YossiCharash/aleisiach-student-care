import { useState, type ReactNode } from "react";
import type { IncidentReportFields } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import { toggled } from "@/lib/utils/arrays";
import {
  ATTACHMENT_NOTE,
  EVENT_SECTIONS,
  LESSON_SECTIONS,
  NATURES,
  REFERRALS,
  REPORT_TYPES,
  shortTime,
} from "@/pages/student/incidents/incidentOptions";

type Update = <K extends keyof IncidentReportFields>(
  key: K,
  value: IncidentReportFields[K]
) => void;

export function IncidentReportForm({
  initial,
  recipient,
  submitLabel,
  pending,
  error,
  onSubmit,
  onCancel,
}: {
  initial: IncidentReportFields;
  recipient: string;
  submitLabel: string;
  pending: boolean;
  error: unknown;
  onSubmit: (fields: IncidentReportFields) => void;
  onCancel: () => void;
}): ReactNode {
  const [draft, setDraft] = useState<IncidentReportFields>(initial);
  const update: Update = (key, value) => setDraft((prev) => ({ ...prev, [key]: value }));
  const canSave = draft.event_date !== "" && draft.description.trim() !== "";

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>פרטי האירוע</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <span className="text-sm text-ink-muted">שם מקבל השירות המעורב באירוע</span>
            <p className="font-medium text-ink">{recipient}</p>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div>
              <Label htmlFor="ir-event-date">תאריך האירוע</Label>
              <Input
                id="ir-event-date"
                type="date"
                value={draft.event_date}
                onChange={(event) => update("event_date", event.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="ir-event-time">שעת האירוע</Label>
              <Input
                id="ir-event-time"
                type="time"
                value={shortTime(draft.event_time)}
                onChange={(event) => update("event_time", event.target.value || null)}
              />
            </div>
            <div className="col-span-2">
              <Label htmlFor="ir-location">מקום האירוע</Label>
              <Input
                id="ir-location"
                value={draft.location}
                maxLength={300}
                onChange={(event) => update("location", event.target.value)}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="ir-reporter">שם המדווח ותפקידו</Label>
            <Input
              id="ir-reporter"
              value={draft.reporter_name_role}
              maxLength={300}
              onChange={(event) => update("reporter_name_role", event.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>מהות האירוע</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <fieldset>
            <legend className="mb-2 text-sm font-medium text-ink">סוג האירוע</legend>
            <div className="flex flex-wrap gap-6">
              {REPORT_TYPES.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-2 text-sm text-ink"
                >
                  <input
                    type="checkbox"
                    className="h-4 w-4"
                    checked={draft.report_type === option.value}
                    onChange={(event) =>
                      update("report_type", event.target.checked ? option.value : null)
                    }
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend className="mb-2 text-sm font-medium text-ink">
              סמנו את האירוע בסעיף המתאים
            </legend>
            <div className="space-y-2">
              {NATURES.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-2 text-sm text-ink"
                >
                  <input
                    type="checkbox"
                    className="h-4 w-4"
                    checked={draft.natures.includes(option.value)}
                    onChange={(event) =>
                      update(
                        "natures",
                        toggled(draft.natures, option.value, event.target.checked)
                      )
                    }
                  />
                  {option.label}
                </label>
              ))}
            </div>
            {draft.natures.includes("other") && (
              <Input
                aria-label="מהות האירוע — אחר"
                placeholder="פירוט"
                className="mt-2"
                value={draft.nature_other}
                maxLength={300}
                onChange={(event) => update("nature_other", event.target.value)}
              />
            )}
          </fieldset>
          <TextSections draft={draft} update={update} sections={EVENT_SECTIONS} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>החלטה</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <fieldset>
            <legend className="mb-2 text-sm font-medium text-ink">האירוע הועבר ל:</legend>
            <div className="grid grid-cols-2 gap-2 md:grid-cols-3">
              {REFERRALS.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-2 text-sm text-ink"
                >
                  <input
                    type="checkbox"
                    className="h-4 w-4"
                    checked={draft.referrals.includes(option.value)}
                    onChange={(event) =>
                      update(
                        "referrals",
                        toggled(draft.referrals, option.value, event.target.checked)
                      )
                    }
                  />
                  {option.label}
                </label>
              ))}
            </div>
            {draft.referrals.includes("other") && (
              <Input
                aria-label="הועבר ל — אחר"
                placeholder="פירוט"
                className="mt-2"
                value={draft.referral_other}
                maxLength={300}
                onChange={(event) => update("referral_other", event.target.value)}
              />
            )}
          </fieldset>
          <div>
            <Label htmlFor="ir-decision-reasons">נימוקים להחלטה</Label>
            <Textarea
              id="ir-decision-reasons"
              value={draft.decision_reasons}
              maxLength={5000}
              onChange={(event) => update("decision_reasons", event.target.value)}
              className="min-h-24"
            />
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <div>
              <Label htmlFor="ir-manager-date">
                מנהל המפעל / מנהל מקצועי עודכן בתאריך
              </Label>
              <Input
                id="ir-manager-date"
                type="date"
                value={draft.manager_updated_date ?? ""}
                onChange={(event) =>
                  update("manager_updated_date", event.target.value || null)
                }
              />
            </div>
            <div>
              <Label htmlFor="ir-manager-time">בשעה</Label>
              <Input
                id="ir-manager-time"
                type="time"
                value={shortTime(draft.manager_updated_time)}
                onChange={(event) =>
                  update("manager_updated_time", event.target.value || null)
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>הפקת לקחים מהאירוע</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <TextSections draft={draft} update={update} sections={LESSON_SECTIONS} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>ממלא הטופס</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-ink-muted">ימולא ע״י מי שנכח באירוע.</p>
          <div className="max-w-sm">
            <Label htmlFor="ir-filler-role">תפקיד</Label>
            <Input
              id="ir-filler-role"
              value={draft.filler_role}
              maxLength={300}
              onChange={(event) => update("filler_role", event.target.value)}
            />
          </div>
          <p className="text-sm text-ink-muted">{ATTACHMENT_NOTE}</p>
        </CardContent>
      </Card>

      {error ? <Alert tone="error">{errorMessage(error)}</Alert> : null}

      <div className="flex justify-start gap-2">
        <Button onClick={() => onSubmit(draft)} disabled={pending || !canSave}>
          {pending ? "שומר…" : submitLabel}
        </Button>
        <Button variant="outline" onClick={onCancel} disabled={pending}>
          ביטול
        </Button>
      </div>
    </div>
  );
}

function TextSections({
  draft,
  update,
  sections,
}: {
  draft: IncidentReportFields;
  update: Update;
  sections: typeof EVENT_SECTIONS;
}): ReactNode {
  return (
    <>
      {sections.map((section) => (
        <div key={section.key}>
          <Label htmlFor={`ir-${section.key}`}>{section.title}</Label>
          <Textarea
            id={`ir-${section.key}`}
            value={draft[section.key]}
            maxLength={5000}
            onChange={(event) => update(section.key, event.target.value)}
            className="min-h-24"
          />
        </div>
      ))}
    </>
  );
}
