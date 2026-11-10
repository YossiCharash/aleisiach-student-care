import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, ChevronDown, ChevronUp, Pencil, Plus } from "lucide-react";
import { medicalSummaryApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  MedicalSummaryEntryResponse,
  MedicalSummaryFields,
  MedicalSummaryHistoryResponse,
} from "@/lib/api/types";
import { formatDate } from "@/lib/utils/hebrew";
import { todayIso } from "@/lib/utils/dates";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";
import { PdfButton } from "@/components/PdfButton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/Dialog";
import { MedicalSummaryForm } from "@/pages/student/medical/MedicalSummaryForm";
import {
  EMPTY_FIELDS,
  OPTIONS,
  SECTIONS,
  toFields,
  type LayoutItem,
} from "@/pages/student/medical/medicalSummaryLayout";

export function MedicalSummaryTab({ studentId }: { studentId: string }): ReactNode {
  const [creating, setCreating] = useState(false);
  const query = useQuery({
    queryKey: queryKeys.medicalSummary(studentId),
    queryFn: () => medicalSummaryApi.list(studentId),
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

  const history = query.data;
  const entries = history.entries;
  const identity = <IdentityCard history={history} />;

  if (creating) {
    return (
      <NewSummary
        studentId={studentId}
        latest={entries[0]}
        identity={identity}
        onDone={() => setCreating(false)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">סיכום מידע רפואי</h2>
        <div className="flex items-center gap-2">
          {entries.length > 0 && (
            <PdfButton
              url={medicalSummaryApi.combinedPdfUrl(studentId)}
              label="דוח מרוכז"
            />
          )}
          <Button onClick={() => setCreating(true)}>
            <Plus className="h-4 w-4" />
            סיכום מידע רפואי חדש
          </Button>
        </div>
      </div>

      {identity}

      {entries.length === 0 ? (
        <EmptyState>עדיין לא מולא סיכום מידע רפואי לחניך.</EmptyState>
      ) : (
        <div className="space-y-4">
          {entries.map((entry, index) => (
            <EntryCard
              key={entry.id}
              studentId={studentId}
              entry={entry}
              identity={identity}
              initiallyOpen={index === 0}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function useInvalidate(studentId: string): () => void {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.medicalSummary(studentId) });
  };
}

function NewSummary({
  studentId,
  latest,
  identity,
  onDone,
}: {
  studentId: string;
  latest: MedicalSummaryEntryResponse | undefined;
  identity: ReactNode;
  onDone: () => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: ({ fields, date }: { fields: MedicalSummaryFields; date: string }) =>
      medicalSummaryApi.create(studentId, { ...fields, summary_date: date }),
    onSuccess: () => {
      invalidate();
      onDone();
    },
  });

  return (
    <div className="space-y-3">
      <h3 className="text-base font-semibold text-ink">סיכום מידע רפואי חדש</h3>
      {latest && (
        <p className="text-sm text-ink-muted">
          הטופס מולא מראש מהסיכום האחרון ({formatDate(latest.summary_date)}). הסיכום הקודם
          נשמר בהיסטוריה ללא שינוי.
        </p>
      )}
      <MedicalSummaryForm
        initial={latest ? toFields(latest) : EMPTY_FIELDS}
        initialDate={todayIso()}
        identity={identity}
        pending={mutation.isPending}
        error={mutation.error}
        onSubmit={(fields, date) => mutation.mutate({ fields, date })}
        onCancel={onDone}
      />
    </div>
  );
}

function EntryCard({
  studentId,
  entry,
  identity,
  initiallyOpen,
}: {
  studentId: string;
  entry: MedicalSummaryEntryResponse;
  identity: ReactNode;
  initiallyOpen: boolean;
}): ReactNode {
  const [open, setOpen] = useState(initiallyOpen);
  const [editing, setEditing] = useState(false);
  const [archiveOpen, setArchiveOpen] = useState(false);
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: (fields: MedicalSummaryFields) =>
      medicalSummaryApi.update(studentId, entry.id, fields),
    onSuccess: () => {
      invalidate();
      setEditing(false);
    },
  });

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <CardTitle>{formatDate(entry.summary_date)}</CardTitle>
          {entry.author_name && (
            <p className="mt-1 text-xs text-ink-muted">
              נכתב על ידי: {entry.author_name}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <PdfButton url={medicalSummaryApi.pdfUrl(studentId, entry.id)} />
          {!editing && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setOpen(true);
                  setEditing(true);
                }}
              >
                <Pencil className="h-4 w-4" />
                עריכה
              </Button>
              <Button variant="outline" size="sm" onClick={() => setArchiveOpen(true)}>
                <Archive className="h-4 w-4" />
                מחיקה
              </Button>
              <Button
                variant="ghost"
                size="sm"
                aria-expanded={open}
                onClick={() => setOpen((prev) => !prev)}
              >
                {open ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
                {open ? "הסתרה" : "הצגה"}
              </Button>
            </>
          )}
        </div>
      </CardHeader>
      {open && (
        <CardContent>
          {editing ? (
            <MedicalSummaryForm
              initial={toFields(entry)}
              identity={identity}
              pending={mutation.isPending}
              error={mutation.error}
              onSubmit={(fields) => mutation.mutate(fields)}
              onCancel={() => {
                mutation.reset();
                setEditing(false);
              }}
            />
          ) : (
            <EntryView entry={entry} />
          )}
        </CardContent>
      )}

      <ArchiveDialog
        studentId={studentId}
        entryId={entry.id}
        open={archiveOpen}
        onOpenChange={setArchiveOpen}
      />
    </Card>
  );
}

function EntryView({ entry }: { entry: MedicalSummaryEntryResponse }): ReactNode {
  return (
    <div className="space-y-6">
      {SECTIONS.map((section) => (
        <section key={section.title}>
          <h3 className="mb-3 border-b border-slate-100 pb-1 text-base font-semibold text-brand">
            {section.title}
          </h3>
          <dl className="grid grid-cols-1 gap-x-6 gap-y-3 text-sm md:grid-cols-2">
            {section.items.map((item) => (
              <div key={item.key}>
                <dt className="text-ink-muted">{item.label}</dt>
                <dd className="whitespace-pre-wrap font-medium text-ink">
                  {shownValue(item, entry) || "—"}
                </dd>
              </div>
            ))}
          </dl>
          {section.note && <p className="mt-3 text-sm text-ink-muted">{section.note}</p>}
        </section>
      ))}
    </div>
  );
}

function ArchiveDialog({
  studentId,
  entryId,
  open,
  onOpenChange,
}: {
  studentId: string;
  entryId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: () => medicalSummaryApi.archive(studentId, entryId),
    onSuccess: () => {
      invalidate();
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>מחיקת סיכום מידע רפואי</DialogTitle>
          <DialogDescription>
            הסיכום יוסתר מהרשימה ומהדוחות אך יישמר ביומן השינויים ולא יימחק לצמיתות.
          </DialogDescription>
        </DialogHeader>
        {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
        <div className="mt-4 flex justify-start gap-2">
          <Button
            variant="danger"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "מוחק…" : "כן, למחוק"}
          </Button>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            ביטול
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function shownValue(item: LayoutItem, entry: MedicalSummaryEntryResponse): string {
  switch (item.kind) {
    case "text":
      return entry[item.key];
    case "date":
      return entry[item.key] ? formatDate(entry[item.key]) : "";
    case "flag": {
      const value = entry[item.key];
      return value === null ? "" : value ? "כן" : "לא";
    }
    case "options": {
      const labels = OPTIONS[item.key]
        .filter((option) => entry[item.key].includes(option.value))
        .map((option) =>
          item.other && option.value === item.other.when && entry[item.other.key]
            ? `${option.label}: ${entry[item.other.key]}`
            : option.label
        );
      return labels.join(" · ");
    }
  }
}

function IdentityCard({
  history,
}: {
  history: MedicalSummaryHistoryResponse;
}): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>פרטי החניך</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-4">
          <IdentityField label="שם" value={history.student_name} />
          <IdentityField label="מספר זהות" value={history.national_id} />
          <IdentityField label="תאריך לידה" value={formatDate(history.date_of_birth)} />
          <IdentityField label="כתובת" value={history.address} />
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
