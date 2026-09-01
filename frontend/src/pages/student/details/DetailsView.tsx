import type { ReactNode } from "react";
import type { ContactInfo, StudentDetailsResponse } from "@/lib/api/types";
import { formatDate, IDD_DIAGNOSIS_NAME, legalStatusLabels } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/ErrorState";
import { Badge } from "@/components/ui/Badge";

export function DetailsView({ details }: { details: StudentDetailsResponse }): ReactNode {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>זהות</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
            <Field label="תעודת זהות" value={details.national_id} />
            <Field label="תאריך לידה" value={formatDate(details.date_of_birth)} />
            <Field
              label="גיל"
              value={details.age !== null ? String(details.age) : null}
            />
            <Field label="שפת דיבור עיקרית בבית" value={details.home_language} />
            <div className="col-span-2">
              <Field label="כתובת" value={details.address} />
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>אבחונים</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="rounded-lg border border-slate-100 px-3 py-2">
            <div className="font-medium text-ink">{IDD_DIAGNOSIS_NAME}</div>
            <div className="mt-0.5 text-sm text-ink-muted">
              דרגה: {details.idd_severity || "—"}
            </div>
          </div>
          {details.additional_diagnoses.length > 0 && (
            <ul className="space-y-1">
              {details.additional_diagnoses.map((name) => (
                <li
                  key={name}
                  className="rounded-lg border border-slate-100 px-3 py-2 text-sm text-ink"
                >
                  {name}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>אנשי קשר לחירום</CardTitle>
        </CardHeader>
        <CardContent>
          <ContactList contacts={details.emergency_contacts} />
        </CardContent>
      </Card>

      <MedicalProfileCard details={details} />

      <Card>
        <CardHeader>
          <CardTitle>ערוץ תקשורת מועדף</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div>
            <span className="text-ink-muted">אופן הבעה עיקרי: </span>
            <span className="font-medium text-ink">{details.expression_mode || "—"}</span>
          </div>
          <div>
            <span className="text-ink-muted">מידת הבנת השפה: </span>
            <span className="font-medium text-ink">
              {details.language_comprehension || "—"}
            </span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>רקע חינוכי ותעסוקתי קודם</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <TextBlock
            label="מסגרת נוכחית או אחרונה"
            value={details.current_or_last_framework}
          />
          <TextBlock
            label="ניסיון קודם במטלות / עבודות"
            value={details.prior_task_experience}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>תעודת זהות רגשית</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <TextBlock label="תחומי עניין וחוזקות" value={details.interests_strengths} />
          <TextBlock label="גורמים מציפים / טריגרים" value={details.triggers} />
          <TextBlock label="סימנים מקדימים למצוקה" value={details.distress_early_signs} />
          <TextBlock label="דרכי הרגעה מומלצות" value={details.calming_methods} />
        </CardContent>
      </Card>

      {details.sensitive_visible ? (
        <Card>
          <CardHeader>
            <CardTitle>אפוטרופסות ומעמד משפטי</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm">
              <span className="text-ink-muted">מעמד משפטי: </span>
              <span className="font-medium text-ink">
                {details.legal_status ? legalStatusLabels[details.legal_status] : "—"}
              </span>
            </div>
            <div>
              <div className="mb-1 text-sm text-ink-muted">אפוטרופוסים</div>
              <ContactList contacts={details.guardians} />
            </div>
          </CardContent>
        </Card>
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

function MedicalProfileCard({ details }: { details: StudentDetailsResponse }): ReactNode {
  const devices = [...details.assistive_devices];
  if (details.assistive_device_other) {
    devices.push(`אחר: ${details.assistive_device_other}`);
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>פרופיל רפואי ובטיחותי קריטי</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <ListBlock
          label="אלרגיות / מגבלות תזונה"
          items={details.has_allergies_or_dietary ? details.allergies_dietary : []}
          emptyLabel={details.has_allergies_or_dietary ? "אין פירוט." : "אין."}
        />
        <ListBlock
          label="תרופות קבועות"
          items={details.takes_regular_medication ? details.medications : []}
          emptyLabel={details.takes_regular_medication ? "אין פירוט." : "אין."}
        />
        {details.takes_regular_medication && (
          <div>
            <span className="text-ink-muted">מידת עצמאות בלקיחת תרופות: </span>
            <span className="font-medium text-ink">
              {details.medication_independence || "—"}
            </span>
          </div>
        )}
        <div>
          <div className="mb-1 text-ink-muted">פרוטוקול חירום רפואי</div>
          <div className="whitespace-pre-wrap font-medium text-ink">
            {details.emergency_protocol || "—"}
          </div>
        </div>
        <ListBlock label="אביזרי עזר פיזיים" items={devices} emptyLabel="אין." />
      </CardContent>
    </Card>
  );
}

function ListBlock({
  label,
  items,
  emptyLabel,
}: {
  label: string;
  items: string[];
  emptyLabel: string;
}): ReactNode {
  return (
    <div>
      <div className="mb-1 text-ink-muted">{label}</div>
      {items.length === 0 ? (
        <div className="text-ink-muted">{emptyLabel}</div>
      ) : (
        <ul className="space-y-1">
          {items.map((item) => (
            <li
              key={item}
              className="rounded-lg border border-slate-100 px-3 py-1.5 text-ink"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function TextBlock({ label, value }: { label: string; value: string | null }): ReactNode {
  return (
    <div>
      <div className="mb-1 text-ink-muted">{label}</div>
      <div className="whitespace-pre-wrap font-medium text-ink">{value || "—"}</div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | null }): ReactNode {
  return (
    <div>
      <dt className="text-ink-muted">{label}</dt>
      <dd className="font-medium text-ink">{value ? value : "—"}</dd>
    </div>
  );
}

function ContactList({ contacts }: { contacts: ContactInfo[] }): ReactNode {
  if (contacts.length === 0) {
    return <EmptyState>אין אנשי קשר.</EmptyState>;
  }
  return (
    <ul className="space-y-2">
      {contacts.map((contact, index) => (
        <li key={index} className="rounded-lg border border-slate-100 px-3 py-2 text-sm">
          <div className="font-medium text-ink">{contact.full_name}</div>
          <div className="text-ink-muted">
            {[contact.relationship, contact.phone].filter(Boolean).join(" · ") || "—"}
          </div>
        </li>
      ))}
    </ul>
  );
}
