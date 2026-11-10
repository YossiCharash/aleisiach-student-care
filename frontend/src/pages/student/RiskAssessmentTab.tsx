import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, ChevronDown, ChevronUp, Pencil, Plus } from "lucide-react";
import { riskAssessmentApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  RiskAssessmentEntryResponse,
  RiskAssessmentRequest,
  RiskDomainInfo,
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
import { RiskAssessmentForm } from "@/pages/student/risks/RiskAssessmentForm";
import { RiskAssessmentView } from "@/pages/student/risks/RiskAssessmentView";
import { emptyRequest, requestOf } from "@/pages/student/risks/riskLevels";

export function RiskAssessmentTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const canWrite = user ? permissions.canWriteRiskAssessments(user) : false;
  const canArchive = user ? permissions.canArchiveRiskAssessments(user) : false;
  const [creating, setCreating] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.riskAssessments(studentId),
    queryFn: () => riskAssessmentApi.list(studentId),
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

  const { domains, entries } = query.data;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">ניהול סיכונים</h2>
        <div className="flex items-center gap-2">
          {entries.length > 0 && (
            <PdfButton
              url={riskAssessmentApi.combinedPdfUrl(studentId)}
              label="דוח מרוכז"
            />
          )}
          {canWrite && !creating && (
            <Button onClick={() => setCreating(true)}>
              <Plus className="h-4 w-4" />
              טבלת ניהול סיכונים חדשה
            </Button>
          )}
        </div>
      </div>

      {creating ? (
        <NewAssessment
          studentId={studentId}
          domains={domains}
          onDone={() => setCreating(false)}
        />
      ) : entries.length === 0 ? (
        <EmptyState>עדיין לא מולאה טבלת ניהול סיכונים לתלמיד.</EmptyState>
      ) : (
        <div className="space-y-4">
          {entries.map((entry, index) => (
            <EntryCard
              key={entry.id}
              studentId={studentId}
              domains={domains}
              entry={entry}
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
      queryKey: queryKeys.riskAssessments(studentId),
    });
  };
}

function NewAssessment({
  studentId,
  domains,
  onDone,
}: {
  studentId: string;
  domains: RiskDomainInfo[];
  onDone: () => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: (request: RiskAssessmentRequest) =>
      riskAssessmentApi.create(studentId, request),
    onSuccess: () => {
      invalidate();
      onDone();
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>טבלת ניהול סיכונים חדשה</CardTitle>
      </CardHeader>
      <CardContent>
        <RiskAssessmentForm
          studentId={studentId}
          domains={domains}
          initial={emptyRequest(domains, todayIso())}
          submitLabel="שמירת הטבלה"
          pending={mutation.isPending}
          error={mutation.error}
          onSubmit={(request) => mutation.mutate(request)}
          onCancel={onDone}
        />
      </CardContent>
    </Card>
  );
}

function EntryCard({
  studentId,
  domains,
  entry,
  canWrite,
  canArchive,
  initiallyOpen,
}: {
  studentId: string;
  domains: RiskDomainInfo[];
  entry: RiskAssessmentEntryResponse;
  canWrite: boolean;
  canArchive: boolean;
  initiallyOpen: boolean;
}): ReactNode {
  const [open, setOpen] = useState(initiallyOpen);
  const [editing, setEditing] = useState(false);
  const [archiveOpen, setArchiveOpen] = useState(false);
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: (request: RiskAssessmentRequest) =>
      riskAssessmentApi.update(studentId, entry.id, request),
    onSuccess: () => {
      invalidate();
      setEditing(false);
    },
  });

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <CardTitle>{formatDate(entry.assessment_date)}</CardTitle>
          {entry.author_name && (
            <p className="mt-1 text-xs text-ink-muted">
              הוזן על ידי: {entry.author_name}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2">
          <PdfButton url={riskAssessmentApi.pdfUrl(studentId, entry.id)} />
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
            <RiskAssessmentForm
              studentId={studentId}
              domains={domains}
              initial={requestOf(domains, entry)}
              submitLabel="שמירה"
              pending={mutation.isPending}
              error={mutation.error}
              onSubmit={(request) => mutation.mutate(request)}
              onCancel={() => setEditing(false)}
            />
          ) : (
            <RiskAssessmentView domains={domains} entry={entry} />
          )}
        </CardContent>
      )}

      {canArchive && (
        <ArchiveDialog
          studentId={studentId}
          assessmentId={entry.id}
          open={archiveOpen}
          onOpenChange={setArchiveOpen}
        />
      )}
    </Card>
  );
}

function ArchiveDialog({
  studentId,
  assessmentId,
  open,
  onOpenChange,
}: {
  studentId: string;
  assessmentId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: () => riskAssessmentApi.archive(studentId, assessmentId),
    onSuccess: () => {
      invalidate();
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>מחיקת טבלת ניהול סיכונים</DialogTitle>
          <DialogDescription>
            הטבלה תוסתר מהרשימה ומהדוחות אך תישמר ביומן השינויים ולא תימחק לצמיתות.
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
