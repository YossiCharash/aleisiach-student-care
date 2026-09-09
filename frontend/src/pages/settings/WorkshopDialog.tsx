import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { usersApi, workshopsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { WorkshopResponse } from "@/lib/api/types";
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

const DEFAULT_COLOR = "#3F8420";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  workshop?: WorkshopResponse;
}

export function WorkshopDialog({ open, onOpenChange, workshop }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [color, setColor] = useState(DEFAULT_COLOR);
  const [instructorId, setInstructorId] = useState("");

  useEffect(() => {
    if (open) {
      setName(workshop?.name ?? "");
      setColor(workshop?.color ?? DEFAULT_COLOR);
      setInstructorId(workshop?.instructor_id ?? "");
    }
  }, [open, workshop?.name, workshop?.color, workshop?.instructor_id]);

  const instructorsQuery = useQuery({
    queryKey: queryKeys.users,
    queryFn: usersApi.list,
    enabled: open,
  });
  const instructors = (instructorsQuery.data ?? []).filter(
    (user) => user.role === "instructor" && user.status !== "disabled"
  );

  const mutation = useMutation({
    mutationFn: () => {
      const body = {
        name: name.trim(),
        color,
        instructor_id: instructorId || null,
      };
      return workshop === undefined
        ? workshopsApi.create(body)
        : workshopsApi.update(workshop.id, body);
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.workshops });
      void queryClient.invalidateQueries({ queryKey: queryKeys.users });
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
          <DialogTitle>{workshop === undefined ? "סדנה חדשה" : "עריכת סדנה"}</DialogTitle>
          <DialogDescription>שם, צבע מזהה ומדריך אחראי לסדנה.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
          <div>
            <Label htmlFor="workshop-name">שם הסדנה</Label>
            <Input
              id="workshop-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="workshop-color">צבע הסדנה</Label>
            <div className="flex items-center gap-3">
              <input
                id="workshop-color"
                type="color"
                value={color}
                onChange={(event) => setColor(event.target.value)}
                className="h-10 w-16 cursor-pointer rounded-xl border border-slate-300 bg-white p-1"
              />
              <span className="text-sm text-ink-muted">{color}</span>
            </div>
          </div>
          <div>
            <Label htmlFor="workshop-instructor">מדריך הסדנה</Label>
            <select
              id="workshop-instructor"
              value={instructorId}
              onChange={(event) => setInstructorId(event.target.value)}
              disabled={instructorsQuery.isLoading || instructorsQuery.isError}
              className="h-10 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm disabled:bg-slate-100"
            >
              <option value="">ללא מדריך</option>
              {instructors.map((instructor) => (
                <option key={instructor.id} value={instructor.id}>
                  {instructor.full_name}
                </option>
              ))}
            </select>
            {instructorsQuery.isError && (
              <p className="mt-1 text-xs text-rating-red">
                {errorMessage(instructorsQuery.error)}
              </p>
            )}
          </div>
          <div className="flex justify-start gap-2">
            <Button type="submit" disabled={mutation.isPending || name.trim() === ""}>
              {mutation.isPending ? "שומר…" : "שמירה"}
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
