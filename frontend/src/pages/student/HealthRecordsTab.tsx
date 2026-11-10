import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Pencil, Plus } from "lucide-react";
import { healthRecordsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  HealthDomainInfo,
  HealthRecordRequest,
  HealthRecordResponse,
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
import { HealthRecordForm } from "@/pages/student/health/HealthRecordForm";
import {
  HEALTH_COLUMNS,
  HEALTH_TITLE,
  emptyRecord,
  requestOf,
  sessionTypeLabel,
} from "@/pages/student/health/healthRecordFields";

type Editing =
  { kind: "new"; domainId: string } | { kind: "edit"; record: HealthRecordResponse };

export function HealthRecordsTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const canWrite = user ? permissions.canWriteHealthRecords(user) : false;
  const canArchive = user ? permissions.canArchiveHealthRecords(user) : false;
  const [editing, setEditing] = useState<Editing | null>(null);

  const query = useQuery({
    queryKey: queryKeys.healthRecords(studentId),
    queryFn: () => healthRecordsApi.list(studentId),
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
  const hasActiveDomain = domains.some((domain) => domain.is_active);
  const usedDomains = domains.filter((domain) =>
    entries.some((entry) => entry.domain_id === domain.id)
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">{HEALTH_TITLE}</h2>
        <div className="flex items-center gap-2">
          {entries.length > 0 && (
            <PdfButton url={healthRecordsApi.pdfUrl(studentId)} label="דוח מרוכז" />
          )}
          {canWrite && hasActiveDomain && (
            <Button onClick={() => setEditing({ kind: "new", domainId: "" })}>
              <Plus className="h-4 w-4" />
              שורת תיעוד חדשה
            </Button>
          )}
        </div>
      </div>

      {!hasActiveDomain && entries.length === 0 ? (
        <EmptyState>
          לא הוגדרו תחומי מקצועות הבריאות. מנהל יכול להוסיף תחומים בדף ההגדרות.
        </EmptyState>
      ) : usedDomains.length === 0 ? (
        <EmptyState>עדיין לא תועדו שורות לתלמיד.</EmptyState>
      ) : (
        usedDomains.map((domain) => (
          <DomainTable
            key={domain.id}
            studentId={studentId}
            domain={domain}
            records={entries.filter((entry) => entry.domain_id === domain.id)}
            canWrite={canWrite}
            canArchive={canArchive}
            onAdd={() => setEditing({ kind: "new", domainId: domain.id })}
            onEdit={(record) => setEditing({ kind: "edit", record })}
          />
        ))
      )}

      {editing && (
        <RecordDialog
          studentId={studentId}
          domains={domains}
          editing={editing}
          onClose={() => setEditing(null)}
        />
      )}
    </div>
  );
}

function useInvalidate(studentId: string): () => void {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.healthRecords(studentId) });
  };
}

function DomainTable({
  studentId,
  domain,
  records,
  canWrite,
  canArchive,
  onAdd,
  onEdit,
}: {
  studentId: string;
  domain: HealthDomainInfo;
  records: HealthRecordResponse[];
  canWrite: boolean;
  canArchive: boolean;
  onAdd: () => void;
  onEdit: (record: HealthRecordResponse) => void;
}): ReactNode {
  const [archiving, setArchiving] = useState<HealthRecordResponse | null>(null);
  const showActions = canWrite || canArchive;

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <CardTitle>תחום: {domain.name}</CardTitle>
        <div className="flex items-center gap-2">
          <PdfButton url={healthRecordsApi.pdfUrl(studentId, domain.id)} />
          {canWrite && domain.is_active && (
            <Button variant="outline" size="sm" onClick={onAdd}>
              <Plus className="h-4 w-4" />
              הוספת שורה
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-brand-600 text-white">
                {HEALTH_COLUMNS.map((title) => (
                  <th key={title} className="p-2 text-start font-medium">
                    {title}
                  </th>
                ))}
                {showActions && (
                  <th className="p-2">
                    <span className="sr-only">פעולות</span>
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id} className="border-b border-slate-200 align-top">
                  <td className="whitespace-nowrap p-2">
                    {formatDate(record.record_date)}
                  </td>
                  <td className="p-2">{sessionTypeLabel(record.session_type)}</td>
                  <td className="whitespace-pre-wrap p-2">{record.support_given}</td>
                  <td className="p-2">
                    {record.responsible.map((member) => member.full_name).join(", ")}
                  </td>
                  <td className="whitespace-pre-wrap p-2">{record.notes}</td>
                  <td className="whitespace-pre-wrap p-2">{record.execution_review}</td>
                  {showActions && (
                    <td className="whitespace-nowrap p-2">
                      {canWrite && (
                        <Button
                          variant="ghost"
                          size="sm"
                          aria-label={`עריכת שורה מ־${formatDate(record.record_date)}`}
                          onClick={() => onEdit(record)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                      )}
                      {canArchive && (
                        <Button
                          variant="ghost"
                          size="sm"
                          aria-label={`מחיקת שורה מ־${formatDate(record.record_date)}`}
                          onClick={() => setArchiving(record)}
                        >
                          <Archive className="h-4 w-4" />
                        </Button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
      {archiving && (
        <ArchiveDialog
          studentId={studentId}
          recordId={archiving.id}
          onClose={() => setArchiving(null)}
        />
      )}
    </Card>
  );
}

function RecordDialog({
  studentId,
  domains,
  editing,
  onClose,
}: {
  studentId: string;
  domains: HealthDomainInfo[];
  editing: Editing;
  onClose: () => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: (request: HealthRecordRequest) =>
      editing.kind === "edit"
        ? healthRecordsApi.update(studentId, editing.record.id, request)
        : healthRecordsApi.create(studentId, request),
    onSuccess: () => {
      invalidate();
      onClose();
    },
  });
  const isEdit = editing.kind === "edit";

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEdit ? "עריכת שורת תיעוד" : "שורת תיעוד חדשה"}</DialogTitle>
          <DialogDescription>{HEALTH_TITLE}</DialogDescription>
        </DialogHeader>
        <HealthRecordForm
          studentId={studentId}
          domains={domains}
          initial={
            isEdit ? requestOf(editing.record) : emptyRecord(editing.domainId, todayIso())
          }
          assignedMembers={isEdit ? editing.record.responsible : []}
          submitLabel={isEdit ? "שמירה" : "הוספת השורה"}
          pending={mutation.isPending}
          error={mutation.error}
          onSubmit={(request) => mutation.mutate(request)}
          onCancel={onClose}
        />
      </DialogContent>
    </Dialog>
  );
}

function ArchiveDialog({
  studentId,
  recordId,
  onClose,
}: {
  studentId: string;
  recordId: string;
  onClose: () => void;
}): ReactNode {
  const invalidate = useInvalidate(studentId);
  const mutation = useMutation({
    mutationFn: () => healthRecordsApi.archive(studentId, recordId),
    onSuccess: () => {
      invalidate();
      onClose();
    },
  });

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>מחיקת שורת תיעוד</DialogTitle>
          <DialogDescription>
            השורה תוסתר מהטבלה ומהדוחות אך תישמר ביומן השינויים ולא תימחק לצמיתות.
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
          <Button variant="ghost" onClick={onClose}>
            ביטול
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
