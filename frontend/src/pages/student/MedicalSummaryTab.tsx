import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import { medicalSummaryApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { MedicalSummaryFields, MedicalSummaryResponse } from "@/lib/api/types";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";
import { MedicalSummaryForm } from "@/pages/student/medical/MedicalSummaryForm";
import {
  OPTIONS,
  SECTIONS,
  toFields,
  type LayoutItem,
} from "@/pages/student/medical/medicalSummaryLayout";

export function MedicalSummaryTab({ studentId }: { studentId: string }): ReactNode {
  const [editing, setEditing] = useState(false);
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: queryKeys.medicalSummary(studentId),
    queryFn: () => medicalSummaryApi.get(studentId),
  });
  const mutation = useMutation({
    mutationFn: (fields: MedicalSummaryFields) =>
      medicalSummaryApi.upsert(studentId, fields),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.medicalSummary(studentId), data);
      setEditing(false);
    },
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

  const summary = query.data;

  if (editing) {
    return (
      <MedicalSummaryForm
        initial={toFields(summary)}
        identity={<IdentityCard summary={summary} />}
        pending={mutation.isPending}
        error={mutation.error}
        onSubmit={(fields) => mutation.mutate(fields)}
        onCancel={() => {
          mutation.reset();
          setEditing(false);
        }}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <PdfButton url={medicalSummaryApi.pdfUrl(studentId)} />
        <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
          <Pencil className="h-4 w-4" />
          {summary.exists ? "עריכה" : "מילוי הטופס"}
        </Button>
      </div>

      <IdentityCard summary={summary} />

      {summary.exists ? (
        <>
          {SECTIONS.map((section) => (
            <Card key={section.title}>
              <CardHeader>
                <CardTitle>{section.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <dl className="grid grid-cols-1 gap-x-6 gap-y-3 text-sm md:grid-cols-2">
                  {section.items.map((item) => (
                    <div key={item.key}>
                      <dt className="text-ink-muted">{item.label}</dt>
                      <dd className="whitespace-pre-wrap font-medium text-ink">
                        {shownValue(item, summary) || "—"}
                      </dd>
                    </div>
                  ))}
                </dl>
                {section.note && (
                  <p className="mt-3 text-sm text-ink-muted">{section.note}</p>
                )}
              </CardContent>
            </Card>
          ))}
          <p className="text-sm text-ink-muted">
            נכתב על ידי {summary.written_by_name ?? "—"}
            {summary.updated_at && ` · עודכן ${formatDate(summary.updated_at)}`}
          </p>
        </>
      ) : (
        <EmptyState>עדיין לא מולא סיכום מידע רפואי לחניך.</EmptyState>
      )}
    </div>
  );
}

function shownValue(item: LayoutItem, summary: MedicalSummaryResponse): string {
  switch (item.kind) {
    case "text":
      return summary[item.key];
    case "date":
      return summary[item.key] ? formatDate(summary[item.key]) : "";
    case "flag": {
      const value = summary[item.key];
      return value === null ? "" : value ? "כן" : "לא";
    }
    case "options": {
      const labels = OPTIONS[item.key]
        .filter((option) => summary[item.key].includes(option.value))
        .map((option) =>
          item.other && option.value === item.other.when && summary[item.other.key]
            ? `${option.label}: ${summary[item.other.key]}`
            : option.label
        );
      return labels.join(" · ");
    }
  }
}

function IdentityCard({ summary }: { summary: MedicalSummaryResponse }): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>סיכום מידע רפואי</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-4">
          <IdentityField label="שם" value={summary.student_name} />
          <IdentityField label="מספר זהות" value={summary.national_id} />
          <IdentityField label="תאריך לידה" value={formatDate(summary.date_of_birth)} />
          <IdentityField label="כתובת" value={summary.address} />
        </dl>
        <p className="mt-3 text-xs text-ink-muted">
          הפרטים נלקחים אוטומטית מלשונית הפרטים האישיים.
        </p>
      </CardContent>
    </Card>
  );
}

function IdentityField({
  label,
  value,
}: {
  label: string;
  value: string | null;
}): ReactNode {
  return (
    <div>
      <dt className="text-ink-muted">{label}</dt>
      <dd className="font-medium text-ink">{value ? value : "—"}</dd>
    </div>
  );
}
