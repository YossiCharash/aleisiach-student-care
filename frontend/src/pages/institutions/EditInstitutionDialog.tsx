import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { institutionsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { InstitutionSummary } from "@/lib/api/types";
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
  institution: InstitutionSummary;
}

export function EditInstitutionDialog({
  open,
  onOpenChange,
  institution,
}: Props): ReactNode {
  const queryClient = useQueryClient();
  const [name, setName] = useState(institution.name);
  const [contactName, setContactName] = useState(institution.contact_name ?? "");
  const [contactPhone, setContactPhone] = useState(institution.contact_phone ?? "");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      institutionsApi.update(institution.id, {
        name: name.trim(),
        contact_name: contactName.trim() || null,
        contact_phone: contactPhone.trim() || null,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.institutions });
      onOpenChange(false);
    },
    onError: (caught) => setError(errorMessage(caught)),
  });

  function handleSubmit(event: FormEvent): void {
    event.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>עריכת מוסד</DialogTitle>
          <DialogDescription>
            קוד המוסד ({institution.code}) קבוע ואינו ניתן לשינוי.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error !== null && <Alert tone="error">{error}</Alert>}

          <div>
            <Label htmlFor="edit-institution-name">שם המוסד</Label>
            <Input
              id="edit-institution-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              required
              minLength={2}
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="edit-institution-contact-name">איש קשר</Label>
            <Input
              id="edit-institution-contact-name"
              value={contactName}
              onChange={(event) => setContactName(event.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="edit-institution-contact-phone">טלפון</Label>
            <Input
              id="edit-institution-contact-phone"
              value={contactPhone}
              onChange={(event) => setContactPhone(event.target.value)}
              dir="ltr"
            />
          </div>

          <div className="flex justify-start gap-2 border-t border-slate-100 pt-4">
            <Button type="submit" disabled={mutation.isPending || name.trim().length < 2}>
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
