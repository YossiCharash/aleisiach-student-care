import type { ReactNode } from "react";
import type { ContactInfo, StudentDetailsResponse } from "@/lib/api/types";
import { formatDate, IDD_DIAGNOSIS_NAME, legalStatusLabels } from "@/lib/utils/hebrew";
import { filled } from "@/lib/utils/text";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  CommunicationChannelCard,
  EmotionalProfileCard,
  TextBlock,
} from "@/pages/student/details/DetailProfileCards";

export function DetailsView({ details }: { details: StudentDetailsResponse }): ReactNode {
  const dob = details.date_of_birth ? formatDate(details.date_of_birth) : null;
  const age = details.age !== null ? String(details.age) : null;

  const devices = [...details.assistive_devices];
  if (details.assistive_device_other) {
    devices.push(`אחר: ${details.assistive_device_other}`);
  }
  const allergies = details.has_allergies_or_dietary ? details.allergies_dietary : [];
  const medications = details.takes_regular_medication ? details.medications : [];
  const independence = details.takes_regular_medication
    ? details.medication_independence
    : null;

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Section
        title="זהות"
        show={[
          details.national_id,
          dob,
          age,
          details.home_language,
          details.address,
        ].some(filled)}
      >
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
          <Field label="תעודת זהות" value={details.national_id} />
          <Field label="תאריך לידה" value={dob} />
          <Field label="גיל" value={age} />
          <Field label="שפת דיבור עיקרית בבית" value={details.home_language} />
          <Field label="כתובת" value={details.address} span2 />
        </dl>
      </Section>

      <Section title="אבחונים" contentClassName="space-y-2">
        <div className="rounded-xl border border-slate-200 px-3.5 py-2.5">
          <div className="font-medium text-ink">{IDD_DIAGNOSIS_NAME}</div>
          {filled(details.idd_severity) && (
            <div className="mt-0.5 text-sm text-ink-muted">
              דרגה: {details.idd_severity}
            </div>
          )}
        </div>
        {filled(details.functioning_level) && (
          <div className="text-sm">
            <span className="text-ink-muted">אוטיזם: </span>
            <span className="font-medium text-ink">{details.functioning_level}</span>
          </div>
        )}
        {details.additional_diagnoses.length > 0 && (
          <ul className="space-y-1">
            {details.additional_diagnoses.map((entry, index) => (
              <li
                key={`${index}-${entry.name}`}
                className="rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm text-ink"
              >
                <span className="font-medium">{entry.name}</span>
                {entry.note && <span className="text-ink-muted"> — {entry.note}</span>}
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="אנשי קשר לחירום" show={details.emergency_contacts.length > 0}>
        <ContactList contacts={details.emergency_contacts} />
      </Section>

      <Section
        title="פרופיל רפואי ובטיחותי קריטי"
        contentClassName="space-y-4 text-sm"
        show={
          allergies.length > 0 ||
          medications.length > 0 ||
          filled(independence) ||
          filled(details.emergency_protocol) ||
          devices.length > 0
        }
      >
        <ListBlock label="אלרגיות / מגבלות תזונה" items={allergies} />
        <ListBlock label="תרופות קבועות" items={medications} />
        {filled(independence) && (
          <div>
            <span className="text-ink-muted">מידת עצמאות בלקיחת תרופות: </span>
            <span className="font-medium text-ink">{independence}</span>
          </div>
        )}
        {filled(details.emergency_protocol) && (
          <div>
            <div className="mb-1 text-ink-muted">פרוטוקול חירום רפואי</div>
            <div className="whitespace-pre-wrap font-medium text-ink">
              {details.emergency_protocol}
            </div>
          </div>
        )}
        <ListBlock label="אביזרי עזר פיזיים" items={devices} />
      </Section>

      <CommunicationChannelCard details={details} />

      <Section
        title="רקע חינוכי ותעסוקתי קודם"
        contentClassName="space-y-4 text-sm"
        show={
          filled(details.previous_institution) || filled(details.prior_task_experience)
        }
      >
        <TextBlock label="מוסד קודם" value={details.previous_institution} />
        <TextBlock label="רקע תעסוקתי קודם" value={details.prior_task_experience} />
      </Section>

      <EmotionalProfileCard details={details} />

      {details.sensitive_visible ? (
        <Section
          title="אפוטרופסות ומעמד משפטי"
          contentClassName="space-y-3"
          show={filled(details.legal_status) || details.guardians.length > 0}
        >
          {details.legal_status && (
            <div className="text-sm">
              <span className="text-ink-muted">מעמד משפטי: </span>
              <span className="font-medium text-ink">
                {legalStatusLabels[details.legal_status]}
              </span>
            </div>
          )}
          {details.guardians.length > 0 && (
            <div>
              <div className="mb-1 text-sm text-ink-muted">אפוטרופוסים</div>
              <ContactList contacts={details.guardians} />
            </div>
          )}
        </Section>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>אפוטרופסות ומעמד משפטי</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge tone="neutral">מידע רגיש — אין הרשאת צפייה</Badge>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function Section({
  title,
  show = true,
  contentClassName,
  children,
}: {
  title: string;
  show?: boolean;
  contentClassName?: string;
  children: ReactNode;
}): ReactNode {
  if (!show) {
    return null;
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className={contentClassName}>{children}</CardContent>
    </Card>
  );
}

function ListBlock({ label, items }: { label: string; items: string[] }): ReactNode {
  if (items.length === 0) {
    return null;
  }
  return (
    <div>
      <div className="mb-1 text-ink-muted">{label}</div>
      <ul className="space-y-1">
        {items.map((item) => (
          <li
            key={item}
            className="rounded-xl border border-slate-200 px-3.5 py-2 text-ink"
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function Field({
  label,
  value,
  span2,
}: {
  label: string;
  value: string | null;
  span2?: boolean;
}): ReactNode {
  if (!filled(value)) {
    return null;
  }
  return (
    <div className={span2 ? "col-span-2" : undefined}>
      <dt className="text-ink-muted">{label}</dt>
      <dd className="font-medium text-ink">{value}</dd>
    </div>
  );
}

function ContactList({ contacts }: { contacts: ContactInfo[] }): ReactNode {
  return (
    <ul className="space-y-2">
      {contacts.map((contact) => (
        <li
          key={`${contact.full_name}-${contact.phone}`}
          className="rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm"
        >
          <div className="font-medium text-ink">{contact.full_name}</div>
          <div className="text-ink-muted">
            {[contact.relationship, contact.phone].filter(Boolean).join(" · ") || "—"}
          </div>
        </li>
      ))}
    </ul>
  );
}
