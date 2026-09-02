import { useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Pencil, Power, X } from "lucide-react";
import { institutionsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { InstitutionSummary } from "@/lib/api/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ConfirmDeactivationDialog } from "@/pages/institutions/ConfirmDeactivationDialog";

export function InstitutionRow({
  institution,
}: {
  institution: InstitutionSummary;
}): ReactNode {
  const queryClient = useQueryClient();
  const [name, setName] = useState(institution.name);
  const [isEditing, setIsEditing] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);

  function refresh(): void {
    void queryClient.invalidateQueries({ queryKey: queryKeys.institutions });
  }

  const rename = useMutation({
    mutationFn: () => institutionsApi.rename(institution.id, name.trim()),
    onSuccess: () => {
      setIsEditing(false);
      refresh();
    },
  });

  const toggleActive = useMutation({
    mutationFn: () =>
      institution.is_active
        ? institutionsApi.deactivate(institution.id)
        : institutionsApi.activate(institution.id),
    onSuccess: () => {
      setConfirmOpen(false);
      refresh();
    },
  });

  function cancelEditing(): void {
    setName(institution.name);
    setIsEditing(false);
  }

  return (
    <tr className="border-b border-slate-50 last:border-0">
      <td className="px-4 py-3 font-medium text-ink">
        {isEditing ? (
          <div className="flex items-center gap-2">
            <Input
              value={name}
              onChange={(event) => setName(event.target.value)}
              aria-label="שם המוסד"
              autoFocus
            />
            <Button
              variant="ghost"
              size="icon"
              title="שמירה"
              onClick={() => rename.mutate()}
              disabled={rename.isPending || name.trim().length < 2}
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" title="ביטול" onClick={cancelEditing}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          institution.name
        )}
      </td>
      <td className="px-4 py-3 text-ink-muted">{institution.code}</td>
      <td className="px-4 py-3 text-ink-muted">{institution.user_count}</td>
      <td className="px-4 py-3 text-ink-muted">{institution.student_count}</td>
      <td className="px-4 py-3">
        <Badge tone={institution.is_active ? "green" : "neutral"}>
          {institution.is_active ? "פעיל" : "מושבת"}
        </Badge>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            title="שינוי שם"
            onClick={() => setIsEditing(true)}
            disabled={isEditing}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            title={institution.is_active ? "השבתת המוסד" : "הפעלת המוסד"}
            onClick={() =>
              institution.is_active ? setConfirmOpen(true) : toggleActive.mutate()
            }
            disabled={toggleActive.isPending}
          >
            <Power className="h-4 w-4" />
          </Button>
        </div>
      </td>

      <ConfirmDeactivationDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        institutionName={institution.name}
        isPending={toggleActive.isPending}
        onConfirm={() => toggleActive.mutate()}
      />
    </tr>
  );
}
