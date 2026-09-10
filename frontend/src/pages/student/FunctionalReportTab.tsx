import { useEffect, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import { functionalReportApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  FunctionalReportResponse,
  FunctionalReportUpsertRequest,
} from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";

type SectionKey = keyof FunctionalReportUpsertRequest;

const SECTIONS: { key: SectionKey; title: string }[] = [
  { key: "general_background", title: "רקע כללי" },
  { key: "vocational_domain", title: "התחום התעסוקתי" },
  { key: "behavioral_emotional_domain", title: "התחום ההתנהגותי-רגשי" },
  { key: "communication_social_domain", title: "התחום התקשורתי-חברתי" },
  { key: "independence_life_skills_domain", title: "תחום עצמאות וכישורי חיים" },
  { key: "summary_recommendations", title: "סיכום והמלצות" },
];

function toDraft(report: FunctionalReportResponse): FunctionalReportUpsertRequest {
  return {
    general_background: report.general_background,
    vocational_domain: report.vocational_domain,
    behavioral_emotional_domain: report.behavioral_emotional_domain,
    communication_social_domain: report.communication_social_domain,
    independence_life_skills_domain: report.independence_life_skills_domain,
    summary_recommendations: report.summary_recommendations,
  };
}

export function FunctionalReportTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const canWrite = user ? permissions.canWriteFunctionalReport(user) : false;
  const [editing, setEditing] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.functionalReport(studentId),
    queryFn: () => functionalReportApi.get(studentId),
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
      <FunctionalReportForm
        studentId={studentId}
        report={report}
        onDone={() => setEditing(false)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <PdfButton url={functionalReportApi.pdfUrl(studentId)} label="ייצוא PDF" />
        {canWrite && (
          <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
            <Pencil className="h-4 w-4" />
            {report.exists ? "עריכה" : "מילוי הדוח"}
          </Button>
        )}
      </div>

      <IdentityCard report={report} />

      {report.exists ? (
        <div className="space-y-4">
          {SECTIONS.map((section) => (
            <Card key={section.key}>
              <CardHeader>
                <CardTitle>{section.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="whitespace-pre-wrap text-sm text-ink">
                  {report[section.key] || "—"}
                </p>
              </CardContent>
            </Card>
          ))}
          <FooterLine report={report} />
        </div>
      ) : (
        <EmptyState>עדיין לא מולא דוח תפקודי לחניך.</EmptyState>
      )}
    </div>
  );
}

function IdentityCard({ report }: { report: FunctionalReportResponse }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>דוח תפקודי</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-3">
          <Field label="שם" value={report.student_name} />
          <Field label="מספר ת.ז" value={report.national_id} />
          <Field label="תאריך לידה" value={formatDate(report.date_of_birth)} />
        </dl>
      </CardContent>
    </Card>
  );
}

function FooterLine({ report }: { report: FunctionalReportResponse }): ReactNode {
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

function FunctionalReportForm({
  studentId,
  report,
  onDone,
}: {
  studentId: string;
  report: FunctionalReportResponse;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState<FunctionalReportUpsertRequest>(() =>
    toDraft(report)
  );

  useEffect(() => {
    setDraft(toDraft(report));
  }, [report]);

  const mutation = useMutation({
    mutationFn: () => functionalReportApi.upsert(studentId, draft),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.functionalReport(studentId), data);
      onDone();
    },
  });

  return (
    <div className="space-y-4">
      <IdentityCard report={report} />
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      {SECTIONS.map((section) => (
        <Card key={section.key}>
          <CardHeader>
            <CardTitle>{section.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={draft[section.key]}
              maxLength={5000}
              onChange={(event) =>
                setDraft((prev) => ({ ...prev, [section.key]: event.target.value }))
              }
              className="min-h-32"
            />
          </CardContent>
        </Card>
      ))}

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
