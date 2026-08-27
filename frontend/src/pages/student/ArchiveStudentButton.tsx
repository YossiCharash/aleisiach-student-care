import { useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Archive } from "lucide-react";
import { studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

export function ArchiveStudentButton({ studentId }: { studentId: string }): ReactNode {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: () => studentsApi.archive(studentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.students });
      navigate("/", { replace: true });
    },
  });

  return (
    <>
      <Button variant="outline" size="sm" onClick={() => setOpen(true)}>
        <Archive className="h-4 w-4" />
        העברה לארכיון
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>העברת תלמיד לארכיון</DialogTitle>
            <DialogDescription>
              התלמיד יוסתר מהרשימה אך לא יימחק. ניתן לשחזר מול מנהל המערכת.
            </DialogDescription>
          </DialogHeader>
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          <div className="mt-4 flex justify-start gap-2">
            <Button
              variant="danger"
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "מעביר…" : "העברה לארכיון"}
            </Button>
            <Button variant="ghost" onClick={() => setOpen(false)}>
              ביטול
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
