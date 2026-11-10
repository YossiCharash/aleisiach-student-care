import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, ChevronDown, ChevronUp, Pencil, Plus } from "lucide-react";
import { incidentReportApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  IncidentReportEntryResponse,
  IncidentReportFields,
  IncidentReportHistoryResponse,
} from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
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
import { IncidentReportForm } from "@/pages/student/incidents/IncidentReportForm";
import { IncidentReportView } from "@/pages/student/incidents/IncidentReportView";
import { emptyIncidentFields } from "@/pages/student/incidents/incidentOptions";

function recipientOf(history: IncidentReportHistoryResponse): string {
  return history.national_id
    ? `${history.student_name}, ת.ז ${history.national_id}`
    : history.student_name;
}

const FIELD_KEYS = Object.keys(emptyIncidentFields("")) as (keyof IncidentReportFields)[];

function fieldsOf(entry: IncidentReportEntryResponse): IncidentReportFields {
  return Object.fromEntries(
    FIELD_KEYS.map((key) => [key, entry[key]])
  ) as unknown as IncidentReportFields;
}

export function IncidentReportTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const canWrite = user ? permissions.canWriteIncidentReports(user) : false;
  const canArchive = user ? permissions.canArchiveIncidentReports(user) : false;
  const [creating, setCreating] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.incidentReports(studentId),
    queryFn: () => incidentReportApi.list(studentId),
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
  const recipient = recipientOf(history);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">דו״ח אירוע חריג</h2>
        <div className="flex items-center gap-2">
          {entries.length > 0 && (
            <PdfButton
              url={incidentReportApi.combinedPdfUrl(studentId)}
              label="דוח מרוכז"
            />
          )}
          {canWrite && !creating && (
            <Button onClick={() => setCreating(true)}>
              <Plus className="h-4 w-4" />
              דיווח אירוע חריג חדש
            </Button>
          )}
        </div>
      </div>

      {creating ? (
        <NewReport
          studentId={studentId}
          recipient={recipient}
          onDone={() => setCreating(false)}
        />
      ) : entries.length === 0 ? (
        <EmptyState>לא דווחו אירועים חריגים לחניך.</EmptyState>
      ) : (
        <div className="space-y-4">
          {entries.map((entry, index) => (
            <EntryCard
              key={entry.id}
              studentId={studentId}
              entry={entry}
              recipient={recipient}
              canWrite={canWrite}
              canArchive={canArchive}
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
    void queryClient.invalidateQueries({
      queryKey: queryKeys.incidentReports(studentId),
    });
  };
}

function NewReport({
  studentId,
  recipient,
  onDone,
}: {
  studentId: string;
  recipient: string;
  onDone: () => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: (fields: IncidentReportFields) =>
      incidentReportApi.create(studentId, fields),
    onSuccess: () => {
      invalidate();
      onDone();
    },
  });

  return (
    <div className="space-y-3">
      <h3 className="text-base font-semibold text-ink">דיווח אירוע חריג חדש</h3>
      <IncidentReportForm
        initial={emptyIncidentFields(todayIso())}
        recipient={recipient}
        submitLabel="שמירת הדו״ח"
        pending={mutation.isPending}
        error={mutation.error}
        onSubmit={(fields) => mutation.mutate(fields)}
        onCancel={onDone}
      />
    </div>
  );
}

function EntryCard({
  studentId,
  entry,
  recipient,
  canWrite,
  canArchive,
  initiallyOpen,
}: {
  studentId: string;
  entry: IncidentReportEntryResponse;
  recipient: string;
  canWrite: boolean;
  canArchive: boolean;
  initiallyOpen: boolean;
}): ReactNode {
  const [open, setOpen] = useState(initiallyOpen);
  const [editing, setEditing] = useState(false);
  const [archiveOpen, setArchiveOpen] = useState(false);
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: (fields: IncidentReportFields) =>
      incidentReportApi.update(studentId, entry.id, fields),
    onSuccess: () => {
      invalidate();
      setEditing(false);
    },
  });

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <CardTitle>{formatDate(entry.event_date)}</CardTitle>
          {entry.author_name && (
            <p className="mt-1 text-xs text-ink-muted">
              הוזן על ידי: {entry.author_name}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <PdfButton url={incidentReportApi.pdfUrl(studentId, entry.id)} />
          {canWrite && !editing && (
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
          )}
          {canArchive && !editing && (
            <Button variant="outline" size="sm" onClick={() => setArchiveOpen(true)}>
              <Archive className="h-4 w-4" />
              מחיקה
            </Button>
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
            <IncidentReportForm
              initial={fieldsOf(entry)}
              recipient={recipient}
              submitLabel="שמירה"
              pending={mutation.isPending}
              error={mutation.error}
              onSubmit={(fields) => mutation.mutate(fields)}
              onCancel={() => setEditing(false)}
            />
          ) : (
            <IncidentReportView entry={entry} recipient={recipient} />
          )}
        </CardContent>
      )}

      {canArchive && (
        <ArchiveDialog
          studentId={studentId}
          reportId={entry.id}
          open={archiveOpen}
          onOpenChange={setArchiveOpen}
        />
      )}
    </Card>
  );
}

function ArchiveDialog({
  studentId,
  reportId,
  open,
  onOpenChange,
}: {
  studentId: string;
  reportId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: () => incidentReportApi.archive(studentId, reportId),
    onSuccess: () => {
      invalidate();
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>מחיקת דו״ח אירוע חריג</DialogTitle>
          <DialogDescription>
            הדו״ח יוסתר מהרשימה ומהדוחות אך יישמר ביומן השינויים ולא יימחק לצמיתות.
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
