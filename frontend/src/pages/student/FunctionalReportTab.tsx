import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, ChevronDown, ChevronUp, Pencil, Plus } from "lucide-react";
import { functionalReportApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  FunctionalReportEntryResponse,
  FunctionalReportHistoryResponse,
  FunctionalReportSections,
} from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
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
import { todayIso } from "@/lib/utils/dates";

type SectionKey = keyof FunctionalReportSections;

const SECTIONS: { key: SectionKey; title: string }[] = [
  { key: "general_background", title: "רקע כללי" },
  { key: "vocational_domain", title: "התחום התעסוקתי" },
  { key: "behavioral_emotional_domain", title: "התחום ההתנהגותי-רגשי" },
  { key: "communication_social_domain", title: "התחום התקשורתי-חברתי" },
  { key: "independence_life_skills_domain", title: "תחום עצמאות וכישורי חיים" },
  { key: "summary_recommendations", title: "סיכום והמלצות" },
];

function sectionsFrom(source: (key: SectionKey) => string): FunctionalReportSections {
  return Object.fromEntries(
    SECTIONS.map((section) => [section.key, source(section.key)])
  ) as unknown as FunctionalReportSections;
}

const EMPTY_SECTIONS: FunctionalReportSections = sectionsFrom(() => "");

function sectionsOf(entry: FunctionalReportEntryResponse): FunctionalReportSections {
  return sectionsFrom((key) => entry[key]);
}

function hasContent(sections: FunctionalReportSections): boolean {
  return SECTIONS.some((section) => sections[section.key].trim() !== "");
}

export function FunctionalReportTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const canWrite = user ? permissions.canWriteFunctionalReport(user) : false;
  const [creating, setCreating] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.functionalReport(studentId),
    queryFn: () => functionalReportApi.list(studentId),
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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">דוח תפקודי</h2>
        <div className="flex items-center gap-2">
          {entries.length > 0 && (
            <PdfButton
              url={functionalReportApi.combinedPdfUrl(studentId)}
              label="דוח מרוכז"
            />
          )}
          {canWrite && !creating && (
            <Button onClick={() => setCreating(true)}>
              <Plus className="h-4 w-4" />
              דוח תפקודי חדש
            </Button>
          )}
        </div>
      </div>

      <IdentityCard history={history} />

      {creating ? (
        <NewReportForm studentId={studentId} onDone={() => setCreating(false)} />
      ) : entries.length === 0 ? (
        <EmptyState>עדיין לא מולא דוח תפקודי לחניך.</EmptyState>
      ) : (
        <div className="space-y-4">
          {entries.map((entry, index) => (
            <EntryCard
              key={entry.id}
              studentId={studentId}
              entry={entry}
              canWrite={canWrite}
              initiallyOpen={index === 0}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function IdentityCard({
  history,
}: {
  history: FunctionalReportHistoryResponse;
}): ReactNode {
  return (
    <Card>
      <CardContent className="pt-5">
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm md:grid-cols-3">
          <Field label="שם" value={history.student_name} />
          <Field label="מספר ת.ז" value={history.national_id} />
          <Field label="תאריך לידה" value={formatDate(history.date_of_birth)} />
        </dl>
      </CardContent>
    </Card>
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

function EntryCard({
  studentId,
  entry,
  canWrite,
  initiallyOpen,
}: {
  studentId: string;
  entry: FunctionalReportEntryResponse;
  canWrite: boolean;
  initiallyOpen: boolean;
}): ReactNode {
  const [open, setOpen] = useState(initiallyOpen);
  const [editing, setEditing] = useState(false);
  const [archiveOpen, setArchiveOpen] = useState(false);

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <CardTitle>{formatDate(entry.report_date)}</CardTitle>
          {entry.author_name && (
            <p className="mt-1 text-xs text-ink-muted">
              נכתב על ידי: {entry.author_name}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <PdfButton url={functionalReportApi.pdfUrl(studentId, entry.id)} />
          {canWrite && !editing && (
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
            </>
          )}
          {!editing && (
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
          )}
        </div>
      </CardHeader>
      {open && (
        <CardContent>
          {editing ? (
            <EditEntryForm
              studentId={studentId}
              entry={entry}
              onDone={() => setEditing(false)}
            />
          ) : (
            <div className="space-y-4">
              {SECTIONS.map((section) => (
                <div key={section.key}>
                  <h3 className="text-sm font-semibold text-ink">{section.title}</h3>
                  <p className="mt-1 whitespace-pre-wrap text-sm text-ink">
                    {entry[section.key] || "—"}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      )}

      {canWrite && (
        <ArchiveEntryDialog
          studentId={studentId}
          entryId={entry.id}
          open={archiveOpen}
          onOpenChange={setArchiveOpen}
        />
      )}
    </Card>
  );
}

function SectionFields({
  draft,
  onChange,
}: {
  draft: FunctionalReportSections;
  onChange: (key: SectionKey, value: string) => void;
}): ReactNode {
  return (
    <div className="space-y-4">
      {SECTIONS.map((section) => (
        <div key={section.key}>
          <Label htmlFor={`fr-${section.key}`}>{section.title}</Label>
          <Textarea
            id={`fr-${section.key}`}
            value={draft[section.key]}
            maxLength={5000}
            onChange={(event) => onChange(section.key, event.target.value)}
            className="min-h-32"
          />
        </div>
      ))}
    </div>
  );
}

function NewReportForm({
  studentId,
  onDone,
}: {
  studentId: string;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [reportDate, setReportDate] = useState(todayIso);
  const [draft, setDraft] = useState<FunctionalReportSections>(EMPTY_SECTIONS);

  const mutation = useMutation({
    mutationFn: () =>
      functionalReportApi.create(studentId, { report_date: reportDate, ...draft }),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.functionalReport(studentId),
      });
      onDone();
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>דוח תפקודי חדש</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-ink-muted">
          הדוח נשמר עם תאריך ונוסף להיסטוריה. דוחות קודמים נשמרים.
        </p>
        <div className="max-w-xs">
          <Label htmlFor="report-date">תאריך הדוח</Label>
          <Input
            id="report-date"
            type="date"
            value={reportDate}
            onChange={(event) => setReportDate(event.target.value)}
          />
        </div>

        <SectionFields
          draft={draft}
          onChange={(key, value) => setDraft((prev) => ({ ...prev, [key]: value }))}
        />

        {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

        <div className="flex justify-start gap-2 border-t border-slate-100 pt-4">
          <Button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || reportDate === "" || !hasContent(draft)}
          >
            {mutation.isPending ? "שומר…" : "שמירת הדוח"}
          </Button>
          <Button variant="outline" onClick={onDone} disabled={mutation.isPending}>
            ביטול
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function EditEntryForm({
  studentId,
  entry,
  onDone,
}: {
  studentId: string;
  entry: FunctionalReportEntryResponse;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState<FunctionalReportSections>(() => sectionsOf(entry));

  const mutation = useMutation({
    mutationFn: () => functionalReportApi.update(studentId, entry.id, draft),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.functionalReport(studentId),
      });
      onDone();
    },
  });

  return (
    <div className="space-y-4">
      <SectionFields
        draft={draft}
        onChange={(key, value) => setDraft((prev) => ({ ...prev, [key]: value }))}
      />
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
      <div className="flex justify-start gap-2">
        <Button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending || !hasContent(draft)}
        >
          {mutation.isPending ? "שומר…" : "שמירה"}
        </Button>
        <Button variant="outline" onClick={onDone} disabled={mutation.isPending}>
          ביטול
        </Button>
      </div>
    </div>
  );
}

function ArchiveEntryDialog({
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
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => functionalReportApi.archive(studentId, entryId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.functionalReport(studentId),
      });
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>מחיקת דוח תפקודי</DialogTitle>
          <DialogDescription>
            הדוח יוסתר מהרשימה ומהדוחות אך יישמר ביומן השינויים ולא יימחק לצמיתות.
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
