import { useEffect, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import { receptionReportApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  ReceptionChecklistItem,
  ReceptionReportResponse,
  ReceptionReportUpsertRequest,
} from "@/lib/api/types";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";

type ChecklistKey =
  | "committee_held"
  | "director_approval"
  | "family_guardian_housing_updated"
  | "community_social_worker_updated"
  | "management_updated";

const CHECKLIST: { key: ChecklistKey; title: string }[] = [
  { key: "committee_held", title: "התקיימה ועדת קבלה על פי הנוהל?" },
  { key: "director_approval", title: "התקבל אישור של המנהלת לקליטה?" },
  { key: "family_guardian_housing_updated", title: "המשפחה/האפוטרופוס/דיור עודכנו?" },
  { key: "community_social_worker_updated", title: "העו״ס בקהילה עודכנה?" },
  { key: "management_updated", title: "ההנהלה עודכנה?" },
];

function toDraft(report: ReceptionReportResponse): ReceptionReportUpsertRequest {
  return {
    committee_date: report.committee_date,
    committee_participants: report.committee_participants,
    intake_date: report.intake_date,
    committee_summary: report.committee_summary,
    committee_recommendations: report.committee_recommendations,
    framework_code: report.framework_code,
    tariff_code: report.tariff_code,
    committee_held: report.committee_held,
    director_approval: report.director_approval,
    family_guardian_housing_updated: report.family_guardian_housing_updated,
    community_social_worker_updated: report.community_social_worker_updated,
    management_updated: report.management_updated,
  };
}

export function ReceptionReportTab({ studentId }: { studentId: string }): ReactNode {
  const [editing, setEditing] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.receptionReport(studentId),
    queryFn: () => receptionReportApi.get(studentId),
  });

  if (query.isLoading) {
    return <LoadingState />;
  }
  if (query.isError) {
    return <ErrorState error={query.error} />;
  }
  if (!query.data) {
    return null;
  }

  const report = query.data;

  if (editing) {
    return (
      <ReceptionReportForm
        studentId={studentId}
        report={report}
        onDone={() => setEditing(false)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <PdfButton url={receptionReportApi.pdfUrl(studentId)} label="ייצוא PDF" />
        <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
          <Pencil className="h-4 w-4" />
          {report.exists ? "עריכה" : "מילוי הדוח"}
        </Button>
      </div>

      <IdentityCard report={report} />

      {report.exists ? (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>פרטי קליטה</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid grid-cols-1 gap-x-4 gap-y-3 text-sm md:grid-cols-2">
                <Field
                  label="תאריך ועדת קבלה"
                  value={formatDate(report.committee_date)}
                />
                <Field label="תאריך קליטה" value={formatDate(report.intake_date)} />
                <Field label="משתתפי ועדת קבלה" value={report.committee_participants} />
                <Field label="סמל מסגרת" value={report.framework_code} />
                <Field label="סמל תעריף" value={report.tariff_code} />
              </dl>
              <TextBlock label="סיכום ועדת קבלה" value={report.committee_summary} />
              <TextBlock label="המלצות הוועדה" value={report.committee_recommendations} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>בקרת תהליך לביצוע נוהל קבלת מקבל שירות</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-sm">
                {CHECKLIST.map((item) => (
                  <ChecklistRow
                    key={item.key}
                    title={item.title}
                    value={report[item.key]}
                  />
                ))}
              </ul>
            </CardContent>
          </Card>

          <FooterLine report={report} />
        </div>
      ) : (
        <EmptyState>עדיין לא מולא דוח קבלה לחניך.</EmptyState>
      )}
    </div>
  );
}

function IdentityCard({ report }: { report: ReceptionReportResponse }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>דוח קבלה</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-3">
          <Field label="שם העובד/ת" value={report.student_name} />
          <Field label="מספר זהות" value={report.national_id} />
          <Field label="תאריך לידה" value={formatDate(report.date_of_birth)} />
        </dl>
      </CardContent>
    </Card>
  );
}

function ChecklistRow({
  title,
  value,
}: {
  title: string;
  value: ReceptionChecklistItem;
}): ReactNode {
  return (
    <li className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
      <span className="font-medium text-ink">{title}</span>
      <span className={value.done ? "text-brand" : "text-ink-muted"}>
        {value.done ? "בוצע" : "לא בוצע"}
      </span>
      {value.note && <span className="text-ink-muted">— {value.note}</span>}
    </li>
  );
}

function FooterLine({ report }: { report: ReceptionReportResponse }): ReactNode {
  return (
    <div className="flex flex-wrap gap-x-6 gap-y-1 text-xs text-ink-muted">
      {report.written_by_name && <span>נכתב על ידי: {report.written_by_name}</span>}
      {report.updated_at && <span>עודכן לאחרונה: {formatDate(report.updated_at)}</span>}
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

function TextBlock({ label, value }: { label: string; value: string }): ReactNode {
  return (
    <div className="mt-3">
      <p className="text-ink-muted">{label}</p>
      <p className="whitespace-pre-wrap text-sm text-ink">{value || "—"}</p>
    </div>
  );
}

function ReceptionReportForm({
  studentId,
  report,
  onDone,
}: {
  studentId: string;
  report: ReceptionReportResponse;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState<ReceptionReportUpsertRequest>(() => toDraft(report));

  useEffect(() => {
    setDraft(toDraft(report));
  }, [report]);

  const mutation = useMutation({
    mutationFn: () => receptionReportApi.upsert(studentId, draft),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.receptionReport(studentId), data);
      onDone();
    },
  });

  const setField = <K extends keyof ReceptionReportUpsertRequest>(
    key: K,
    value: ReceptionReportUpsertRequest[K]
  ): void => setDraft((prev) => ({ ...prev, [key]: value }));

  const setChecklist = (
    key: ChecklistKey,
    patch: Partial<ReceptionChecklistItem>
  ): void => setDraft((prev) => ({ ...prev, [key]: { ...prev[key], ...patch } }));

  return (
    <div className="space-y-4">
      <IdentityCard report={report} />
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>פרטי קליטה</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="committee_date">תאריך ועדת קבלה</Label>
              <Input
                id="committee_date"
                type="date"
                value={draft.committee_date ?? ""}
                onChange={(event) =>
                  setField("committee_date", event.target.value || null)
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="intake_date">תאריך קליטה</Label>
              <Input
                id="intake_date"
                type="date"
                value={draft.intake_date ?? ""}
                onChange={(event) => setField("intake_date", event.target.value || null)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="framework_code">סמל מסגרת</Label>
              <Input
                id="framework_code"
                value={draft.framework_code}
                maxLength={100}
                onChange={(event) => setField("framework_code", event.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="tariff_code">סמל תעריף</Label>
              <Input
                id="tariff_code"
                value={draft.tariff_code}
                maxLength={100}
                onChange={(event) => setField("tariff_code", event.target.value)}
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="committee_participants">משתתפי ועדת קבלה</Label>
            <Textarea
              id="committee_participants"
              value={draft.committee_participants}
              maxLength={5000}
              onChange={(event) => setField("committee_participants", event.target.value)}
              className="min-h-20"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="committee_summary">סיכום ועדת קבלה</Label>
            <Textarea
              id="committee_summary"
              value={draft.committee_summary}
              maxLength={5000}
              onChange={(event) => setField("committee_summary", event.target.value)}
              className="min-h-32"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="committee_recommendations">המלצות הוועדה</Label>
            <Textarea
              id="committee_recommendations"
              value={draft.committee_recommendations}
              maxLength={5000}
              onChange={(event) =>
                setField("committee_recommendations", event.target.value)
              }
              className="min-h-32"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>בקרת תהליך לביצוע נוהל קבלת מקבל שירות</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {CHECKLIST.map((item) => (
            <div key={item.key} className="space-y-1.5">
              <label className="flex items-center gap-2 text-sm font-medium text-ink">
                <input
                  type="checkbox"
                  className="h-4 w-4"
                  checked={draft[item.key].done}
                  onChange={(event) =>
                    setChecklist(item.key, { done: event.target.checked })
                  }
                />
                {item.title}
              </label>
              <Input
                aria-label={`הערה: ${item.title}`}
                placeholder="הערה (רשות)"
                value={draft[item.key].note}
                maxLength={1000}
                onChange={(event) => setChecklist(item.key, { note: event.target.value })}
              />
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="flex justify-start gap-2">
        <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
          {mutation.isPending ? "שומר…" : "שמירה"}
        </Button>
        <Button variant="outline" onClick={onDone} disabled={mutation.isPending}>
          ביטול
        </Button>
      </div>
    </div>
  );
}
