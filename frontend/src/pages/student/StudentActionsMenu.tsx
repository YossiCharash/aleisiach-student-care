import { useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Archive, MoreHorizontal, Pencil } from "lucide-react";
import { studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { StudentResponse } from "@/lib/api/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/Dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/DropdownMenu";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";
import { EditStudentDialog } from "@/pages/student/EditStudentDialog";

export function StudentActionsMenu({ student }: { student: StudentResponse }): ReactNode {
  const [editOpen, setEditOpen] = useState(false);
  const [archiveOpen, setArchiveOpen] = useState(false);

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="icon" aria-label="פעולות נוספות">
            <MoreHorizontal className="h-5 w-5" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuItem onSelect={() => setEditOpen(true)}>
            <Pencil className="h-4 w-4" />
            עריכת פרטים
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem tone="danger" onSelect={() => setArchiveOpen(true)}>
            <Archive className="h-4 w-4" />
            העברה לארכיון
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <EditStudentDialog student={student} open={editOpen} onOpenChange={setEditOpen} />
      <ArchiveStudentDialog
        studentId={student.id}
        open={archiveOpen}
        onOpenChange={setArchiveOpen}
      />
    </>
  );
}

function ArchiveStudentDialog({
  studentId,
  open,
  onOpenChange,
}: {
  studentId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}): ReactNode {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const mutation = useMutation({
    mutationFn: () => studentsApi.archive(studentId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.students });
      navigate("/students", { replace: true });
    },
  });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
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
            {mutation.isPending ? "מעביר…" : "כן, להעביר לארכיון"}
          </Button>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            ביטול
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
