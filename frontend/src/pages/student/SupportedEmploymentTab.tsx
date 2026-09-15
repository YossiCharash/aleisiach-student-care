import { useEffect, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import { supportedEmploymentApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  SupportedEmploymentResponse,
  SupportedEmploymentUpsertRequest,
} from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";

type FieldKey = keyof SupportedEmploymentUpsertRequest;

const FIELDS: { key: FieldKey; title: string; multiline: boolean }[] = [
  { key: "workplace", title: "מקום העבודה", multiline: false },
  { key: "address", title: "כתובת", multiline: false },
  { key: "activity_type", title: "סוג הפעילות", multiline: true },
  { key: "work_process", title: "תהליך העבודה", multiline: true },
  { key: "work_environment", title: "סביבת העבודה", multiline: true },
  { key: "required_body_functions", title: "תפקודי גוף נחוצים", multiline: true },
  { key: "hazards_and_safety", title: "סכנות ובטיחות", multiline: true },
  { key: "workplace_contact", title: "איש קשר במקום העבודה", multiline: false },
  { key: "escort_contact", title: "איש קשר מלווה", multiline: false },
  { key: "mobility", title: "ניידות", multiline: false },
  { key: "work_hours", title: "שעת עבודה", multiline: false },
];

function toDraft(report: SupportedEmploymentResponse): SupportedEmploymentUpsertRequest {
  return {
    workplace: report.workplace,
    address: report.address,
    activity_type: report.activity_type,
    work_process: report.work_process,
    work_environment: report.work_environment,
    required_body_functions: report.required_body_functions,
    hazards_and_safety: report.hazards_and_safety,
    workplace_contact: report.workplace_contact,
    escort_contact: report.escort_contact,
    mobility: report.mobility,
    work_hours: report.work_hours,
  };
}

export function SupportedEmploymentTab({ studentId }: { studentId: string }): ReactNode {
  const [editing, setEditing] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.supportedEmployment(studentId),
    queryFn: () => supportedEmploymentApi.get(studentId),
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
      <SupportedEmploymentForm
        studentId={studentId}
        report={report}
        onDone={() => setEditing(false)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <PdfButton url={supportedEmploymentApi.pdfUrl(studentId)} label="ייצוא PDF" />
        <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
          <Pencil className="h-4 w-4" />
          {report.exists ? "עריכה" : "מילוי הטופס"}
        </Button>
      </div>

      {report.exists ? (
        <Card>
          <CardHeader>
            <CardTitle>ניתוח עבודה נתמכת</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3 text-sm">
              {FIELDS.map((field) => (
                <div key={field.key}>
                  <dt className="text-ink-muted">{field.title}</dt>
                  <dd className="whitespace-pre-wrap font-medium text-ink">
                    {report[field.key] || "—"}
                  </dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>
      ) : (
        <EmptyState>עדיין לא מולא ניתוח עבודה נתמכת לחניך.</EmptyState>
      )}
    </div>
  );
}

function SupportedEmploymentForm({
  studentId,
  report,
  onDone,
}: {
  studentId: string;
  report: SupportedEmploymentResponse;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState<SupportedEmploymentUpsertRequest>(() =>
    toDraft(report)
  );

  useEffect(() => {
    setDraft(toDraft(report));
  }, [report]);

  const mutation = useMutation({
    mutationFn: () => supportedEmploymentApi.upsert(studentId, draft),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.supportedEmployment(studentId), data);
      onDone();
    },
  });

  const setField = (key: FieldKey, value: string): void =>
    setDraft((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="space-y-4">
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>ניתוח עבודה נתמכת</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {FIELDS.map((field) => (
            <div key={field.key} className="space-y-1.5">
              <Label htmlFor={field.key}>{field.title}</Label>
              {field.multiline ? (
                <Textarea
                  id={field.key}
                  value={draft[field.key]}
                  maxLength={5000}
                  onChange={(event) => setField(field.key, event.target.value)}
                  className="min-h-24"
                />
              ) : (
                <Input
                  id={field.key}
                  value={draft[field.key]}
                  maxLength={5000}
                  onChange={(event) => setField(field.key, event.target.value)}
                />
              )}
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
