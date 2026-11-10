import type { ReactNode } from "react";
import type { IncidentReportEntryResponse } from "@/lib/api/types";
import { formatDate } from "@/lib/utils/hebrew";
import {
  EVENT_SECTIONS,
  LESSON_SECTIONS,
  NATURES,
  REFERRALS,
  REPORT_TYPES,
  shortTime,
} from "@/pages/student/incidents/incidentOptions";

function chosenLabels<T extends string>(
  options: { value: T; label: string }[],
  chosen: T[],
  otherText: string
): string {
  return options
    .filter((option) => chosen.includes(option.value))
    .map((option) =>
      option.value === "other" && otherText
        ? `${option.label}: ${otherText}`
        : option.label
    )
    .join(" · ");
}

export function IncidentReportView({
  entry,
  recipient,
}: {
  entry: IncidentReportEntryResponse;
  recipient: string;
}): ReactNode {
  const reportType = REPORT_TYPES.find((option) => option.value === entry.report_type);
  const managerUpdated = [
    entry.manager_updated_date ? formatDate(entry.manager_updated_date) : "",
    entry.manager_updated_time ? `בשעה ${shortTime(entry.manager_updated_time)}` : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="space-y-5">
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-3">
        <Field label="שם מקבל השירות המעורב באירוע" value={recipient} />
        <Field label="תאריך האירוע" value={formatDate(entry.event_date)} />
        <Field label="שעת האירוע" value={shortTime(entry.event_time)} />
        <Field label="מקום האירוע" value={entry.location} />
        <Field label="שם המדווח ותפקידו" value={entry.reporter_name_role} />
        <Field label="סוג האירוע" value={reportType?.label ?? ""} />
      </dl>

      <Block title="מהות האירוע">
        {chosenLabels(NATURES, entry.natures, entry.nature_other)}
      </Block>
      {EVENT_SECTIONS.map((section) => (
        <Block key={section.key} title={section.title}>
          {entry[section.key]}
        </Block>
      ))}

      <h3 className="border-b border-slate-100 pb-1 text-base font-semibold text-brand">
        החלטה
      </h3>
      <Block title="האירוע הועבר ל">
        {chosenLabels(REFERRALS, entry.referrals, entry.referral_other)}
      </Block>
      <Block title="נימוקים להחלטה">{entry.decision_reasons}</Block>
      <Block title="מנהל המפעל / מנהל מקצועי עודכן">{managerUpdated}</Block>

      <h3 className="border-b border-slate-100 pb-1 text-base font-semibold text-brand">
        הפקת לקחים מהאירוע
      </h3>
      {LESSON_SECTIONS.map((section) => (
        <Block key={section.key} title={section.title}>
          {entry[section.key]}
        </Block>
      ))}

      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 border-t border-slate-100 pt-4 text-sm">
        <Field label="שם ממלא הטופס" value={entry.filler_name} />
        <Field label="תפקיד" value={entry.filler_role} />
      </dl>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }): ReactNode {
  return (
    <div>
      <dt className="text-ink-muted">{label}</dt>
      <dd className="font-medium text-ink">{value || "—"}</dd>
    </div>
  );
}

function Block({ title, children }: { title: string; children: string }): ReactNode {
  return (
    <div>
      <h4 className="text-sm font-semibold text-ink">{title}</h4>
      <p className="mt-1 whitespace-pre-wrap text-sm text-ink">{children || "—"}</p>
    </div>
  );
}
