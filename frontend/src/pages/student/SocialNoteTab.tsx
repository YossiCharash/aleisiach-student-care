import { useEffect, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { socialNoteApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { formatDate } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState, errorMessage } from "@/components/ui/ErrorState";

export function SocialNoteTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const canWrite = user ? permissions.canWriteSocialNote(user) : false;

  const query = useQuery({
    queryKey: queryKeys.socialNote(studentId),
    queryFn: () => socialNoteApi.get(studentId),
  });

  const [draft, setDraft] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setDraft(query.data?.content ?? "");
  }, [query.data?.content]);

  const mutation = useMutation({
    mutationFn: () => socialNoteApi.upsert(studentId, { content: draft }),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.socialNote(studentId), data);
      setSaved(true);
    },
  });

  if (query.isLoading) {
    return <LoadingState />;
  }
  if (query.isError) {
    return <ErrorState error={query.error} />;
  }

  const note = query.data;

  return (
    <Card>
      <CardHeader>
        <CardTitle>הערת עובד/ת סוציאלי/ת</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {note?.updated_at && (
          <p className="text-xs text-ink-muted">
            עודכן לאחרונה: {formatDate(note.updated_at)}
          </p>
        )}

        {canWrite ? (
          <>
            {mutation.isError && (
              <Alert tone="error">{errorMessage(mutation.error)}</Alert>
            )}
            {saved && !mutation.isPending && <Alert tone="success">ההערה נשמרה.</Alert>}
            <Textarea
              value={draft}
              maxLength={5000}
              onChange={(event) => {
                setDraft(event.target.value);
                setSaved(false);
              }}
              className="min-h-48"
              placeholder="כתבו כאן את הערת העו״ס…"
            />
            <div className="flex justify-start">
              <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
                {mutation.isPending ? "שומר…" : "שמירה"}
              </Button>
            </div>
          </>
        ) : note?.content ? (
          <p className="whitespace-pre-wrap text-sm text-ink">{note.content}</p>
        ) : (
          <EmptyState>אין הערת עו״ס עדיין.</EmptyState>
        )}
      </CardContent>
    </Card>
  );
}
