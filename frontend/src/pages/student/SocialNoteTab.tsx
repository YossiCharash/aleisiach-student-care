import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Archive, Pencil, Plus } from "lucide-react";
import { socialNoteApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { SocialNoteEntryResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
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

function today(): string {
  const now = new Date();
  return new Date(now.getTime() - now.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 10);
}

export function SocialNoteTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const canWrite = user ? permissions.canWriteSocialNote(user) : false;
  const [addOpen, setAddOpen] = useState(false);

  const query = useQuery({
    queryKey: queryKeys.socialNote(studentId),
    queryFn: () => socialNoteApi.list(studentId),
  });

  const entries = query.data?.entries ?? [];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">סיכום עו״ס</h2>
        <div className="flex items-center gap-2">
          {entries.length > 0 && (
            <PdfButton url={socialNoteApi.combinedPdfUrl(studentId)} label="דוח מרוכז" />
          )}
          {canWrite && (
            <Button onClick={() => setAddOpen(true)}>
              <Plus className="h-4 w-4" />
              הערה חדשה
            </Button>
          )}
        </div>
      </div>

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data &&
        (entries.length === 0 ? (
          <EmptyState>אין סיכומי עו״ס עדיין.</EmptyState>
        ) : (
          <div className="space-y-4">
            {entries.map((entry) => (
              <EntryCard
                key={entry.id}
                studentId={studentId}
                entry={entry}
                canWrite={canWrite}
              />
            ))}
          </div>
        ))}

      {canWrite && (
        <AddNoteDialog studentId={studentId} open={addOpen} onOpenChange={setAddOpen} />
      )}
    </div>
  );
}

function EntryCard({
  studentId,
  entry,
  canWrite,
}: {
  studentId: string;
  entry: SocialNoteEntryResponse;
  canWrite: boolean;
}): ReactNode {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [archiveOpen, setArchiveOpen] = useState(false);
  const [draft, setDraft] = useState(entry.content);

  const mutation = useMutation({
    mutationFn: () => socialNoteApi.update(studentId, entry.id, { content: draft }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.socialNote(studentId) });
      setEditing(false);
    },
  });

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <CardTitle>{formatDate(entry.note_date)}</CardTitle>
        <div className="flex items-center gap-2">
          <PdfButton url={socialNoteApi.pdfUrl(studentId, entry.id)} label="ייצוא PDF" />
          {canWrite && !editing && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setDraft(entry.content);
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
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {entry.author_name && (
          <p className="text-xs text-ink-muted">נכתב על ידי: {entry.author_name}</p>
        )}
        {editing ? (
          <div className="space-y-2">
            <Textarea
              className="min-h-40"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="כתבו כאן את סיכום העו״ס…"
            />
            {mutation.isError && (
              <Alert tone="error">{errorMessage(mutation.error)}</Alert>
            )}
            <div className="flex justify-end gap-2">
              <Button
                onClick={() => mutation.mutate()}
                disabled={mutation.isPending || draft.trim() === ""}
              >
                {mutation.isPending ? "שומר…" : "שמירה"}
              </Button>
              <Button variant="ghost" onClick={() => setEditing(false)}>
                ביטול
              </Button>
            </div>
          </div>
        ) : (
          <p className="whitespace-pre-wrap text-sm text-ink">{entry.content}</p>
        )}
      </CardContent>

      {canWrite && (
        <ArchiveNoteDialog
          studentId={studentId}
          entryId={entry.id}
          open={archiveOpen}
          onOpenChange={setArchiveOpen}
        />
      )}
    </Card>
  );
}

function AddNoteDialog({
  studentId,
  open,
  onOpenChange,
}: {
  studentId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}): ReactNode {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>הערת עו״ס חדשה</DialogTitle>
          <DialogDescription>
            ההערה נשמרת עם תאריך ונוספת להיסטוריה. הערות קודמות נשמרות.
          </DialogDescription>
        </DialogHeader>
        {open && <AddNoteForm studentId={studentId} onDone={() => onOpenChange(false)} />}
      </DialogContent>
    </Dialog>
  );
}

function AddNoteForm({
  studentId,
  onDone,
}: {
  studentId: string;
  onDone: () => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const [noteDate, setNoteDate] = useState(today);
  const [content, setContent] = useState("");

  const mutation = useMutation({
    mutationFn: () => socialNoteApi.create(studentId, { note_date: noteDate, content }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.socialNote(studentId) });
      onDone();
    },
  });

  return (
    <div className="space-y-4">
      <div className="max-w-xs">
        <Label htmlFor="note-date">תאריך ההערה</Label>
        <Input
          id="note-date"
          type="date"
          value={noteDate}
          onChange={(event) => setNoteDate(event.target.value)}
        />
      </div>

      <div>
        <Label htmlFor="note-content">הערה</Label>
        <Textarea
          id="note-content"
          className="min-h-40"
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="כתבו כאן את סיכום העו״ס…"
        />
      </div>

      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <div className="flex items-center justify-end gap-2 border-t border-slate-100 pt-4">
        <Button
          onClick={() => mutation.mutate()}
          disabled={mutation.isPending || content.trim() === "" || noteDate === ""}
        >
          {mutation.isPending ? "שומר…" : "שמירת הערה"}
        </Button>
        <Button variant="ghost" onClick={onDone}>
          ביטול
        </Button>
      </div>
    </div>
  );
}

function ArchiveNoteDialog({
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
    mutationFn: () => socialNoteApi.archive(studentId, entryId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.socialNote(studentId) });
      onOpenChange(false);
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>מחיקת הערת עו״ס</DialogTitle>
          <DialogDescription>
            ההערה תוסתר מהרשימה ומהדוחות אך תישמר ביומן השינויים ולא תימחק לצמיתות.
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
