import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { institutionsApi } from "@/lib/api/endpoints";
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

const EMPTY_FORM = {
  name: "",
  code: "",
  managerFullName: "",
  managerEmail: "",
  contactName: "",
  contactPhone: "",
};

export function CreateInstitutionDialog({ open, onOpenChange }: Props): ReactNode {
  const queryClient = useQueryClient();
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      institutionsApi.create({
        name: form.name.trim(),
        code: form.code.trim(),
        manager_full_name: form.managerFullName.trim(),
        manager_email: form.managerEmail.trim(),
        contact_name: form.contactName.trim() || null,
        contact_phone: form.contactPhone.trim() || null,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.institutions });
      handleOpenChange(false);
    },
    onError: (caught) => setError(errorMessage(caught)),
  });

  function handleOpenChange(next: boolean): void {
    if (!next) {
      setForm(EMPTY_FORM);
      setError(null);
    }
    onOpenChange(next);
  }

  function handleSubmit(event: FormEvent): void {
    event.preventDefault();
    setError(null);
    mutation.mutate();
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>הקמת מוסד חדש</DialogTitle>
          <DialogDescription>
            המוסד יוקם עם קטלוג ברירת המחדל, ותישלח הזמנה למנהל/ת המוסד הראשון/ה.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error !== null && <Alert tone="error">{error}</Alert>}

          <div>
            <Label htmlFor="institution-name">שם המוסד</Label>
            <Input
              id="institution-name"
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
              minLength={2}
              autoFocus
            />
          </div>
          <div>
            <Label htmlFor="institution-code">קוד המוסד</Label>
            <Input
              id="institution-code"
              value={form.code}
              onChange={(event) => setForm({ ...form, code: event.target.value })}
              required
              minLength={2}
              pattern="[a-z0-9\-]+"
              dir="ltr"
            />
            <p className="mt-1 text-xs text-ink-muted">
              אותיות אנגליות קטנות, ספרות ומקפים בלבד. משמש לזיהוי פנימי ואינו ניתן
              לשינוי.
            </p>
          </div>
          <div>
            <Label htmlFor="institution-manager-name">שם מנהל/ת המוסד</Label>
            <Input
              id="institution-manager-name"
              value={form.managerFullName}
              onChange={(event) =>
                setForm({ ...form, managerFullName: event.target.value })
              }
              required
              minLength={2}
            />
          </div>
          <div>
            <Label htmlFor="institution-manager-email">דוא״ל מנהל/ת המוסד</Label>
            <Input
              id="institution-manager-email"
              type="email"
              value={form.managerEmail}
              onChange={(event) => setForm({ ...form, managerEmail: event.target.value })}
              required
            />
          </div>

          <div>
            <Label htmlFor="institution-contact-name">איש קשר (לא חובה)</Label>
            <Input
              id="institution-contact-name"
              value={form.contactName}
              onChange={(event) => setForm({ ...form, contactName: event.target.value })}
            />
          </div>
          <div>
            <Label htmlFor="institution-contact-phone">טלפון איש הקשר (לא חובה)</Label>
            <Input
              id="institution-contact-phone"
              value={form.contactPhone}
              onChange={(event) => setForm({ ...form, contactPhone: event.target.value })}
              dir="ltr"
            />
          </div>

          <div className="flex justify-start gap-2 border-t border-slate-100 pt-4">
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? "מקים…" : "הקמת המוסד"}
            </Button>
            <Button type="button" variant="ghost" onClick={() => handleOpenChange(false)}>
              ביטול
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
