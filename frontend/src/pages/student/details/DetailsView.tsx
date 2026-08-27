import type { ReactNode } from "react";
import type { ContactInfo, StudentDetailsResponse } from "@/lib/api/types";
import { formatDate, legalStatusLabels } from "@/lib/utils/hebrew";
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
            <Field label="גיל" value={details.age !== null ? String(details.age) : null} />
            <Field label="שפת בית" value={details.home_language} />
            <div className="col-span-2">
              <Field label="כתובת" value={details.address} />
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>אבחנות רפואיות/תפקודיות</CardTitle>
        </CardHeader>
        <CardContent>
          {details.medical_diagnoses.length === 0 ? (
            <EmptyState>אין אבחנות מתועדות.</EmptyState>
          ) : (
            <ul className="space-y-2">
              {details.medical_diagnoses.map((diagnosis, index) => (
                <li key={index} className="rounded-lg border border-slate-100 px-3 py-2">
                  <div className="font-medium text-ink">{diagnosis.name}</div>
                  {diagnosis.notes && (
                    <div className="mt-0.5 text-sm text-ink-muted">{diagnosis.notes}</div>
                  )}
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
