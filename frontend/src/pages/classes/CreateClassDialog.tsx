import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { classesApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CreateClassDialog({ open, onOpenChange }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");

  const mutation = useMutation({
    mutationFn: () => classesApi.create(name.trim()),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.classes });
      setName("");
      onOpenChange(false);
    },
  });

  function handleSubmit(event: FormEvent): void {
    event.preventDefault();
    mutation.mutate();
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>כיתה חדשה</DialogTitle>
          <DialogDescription>הוספת כיתה חדשה למוסד.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          <div>
            <Label htmlFor="class-name">שם הכיתה</Label>
            <Input
              id="class-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="flex justify-start gap-2">
            <Button type="submit" disabled={mutation.isPending || name.trim() === ""}>
              {mutation.isPending ? "שומר…" : "הוספה"}
            </Button>
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
              ביטול
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
