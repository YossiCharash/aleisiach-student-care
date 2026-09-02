import { useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { MailPlus, Pencil, Power } from "lucide-react";
import { institutionsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { InstitutionSummary } from "@/lib/api/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { errorMessage } from "@/components/ui/ErrorState";
import { ConfirmDeactivationDialog } from "@/pages/institutions/ConfirmDeactivationDialog";
import { EditInstitutionDialog } from "@/pages/institutions/EditInstitutionDialog";

export function InstitutionRow({
  institution,
}: {
  institution: InstitutionSummary;
}): ReactNode {
  const queryClient = useQueryClient();
  const [editOpen, setEditOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  function refresh(): void {
    setActionError(null);
    void queryClient.invalidateQueries({ queryKey: queryKeys.institutions });
  }

  function reportFailure(caught: unknown): void {
    setConfirmOpen(false);
    setActionError(errorMessage(caught));
  }

  const toggleActive = useMutation({
    mutationFn: () =>
      institution.is_active
        ? institutionsApi.deactivate(institution.id)
        : institutionsApi.activate(institution.id),
    onSuccess: () => {
      setConfirmOpen(false);
      refresh();
    },
    onError: reportFailure,
  });

  const resendInvitation = useMutation({
    mutationFn: () => institutionsApi.resendManagerInvitation(institution.id),
    onSuccess: refresh,
    onError: reportFailure,
  });

  return (
    <tr className="border-b border-slate-50 last:border-0">
      <td className="px-4 py-3 font-medium text-ink">
        {institution.name}
        {institution.pending_manager_email !== null && (
          <div className="text-xs font-normal text-ink-muted">
            ממתין לאישור הזמנה: {institution.pending_manager_email}
          </div>
        )}
        {actionError !== null && (
          <div className="text-xs font-normal text-rating-red">{actionError}</div>
        )}
      </td>
      <td className="px-4 py-3 text-ink-muted">{institution.code}</td>
      <td className="px-4 py-3 text-ink-muted">
        {institution.contact_name ?? "—"}
        {institution.contact_phone !== null && (
          <div className="text-xs" dir="ltr">
            {institution.contact_phone}
          </div>
        )}
      </td>
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
            title="עריכת מוסד"
            onClick={() => setEditOpen(true)}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          {institution.pending_manager_email !== null && (
            <Button
              variant="ghost"
              size="icon"
              title="שליחת הזמנה מחדש"
              onClick={() => resendInvitation.mutate()}
              disabled={resendInvitation.isPending}
            >
              <MailPlus className="h-4 w-4" />
            </Button>
          )}
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

      {editOpen && (
        <EditInstitutionDialog
          open
          onOpenChange={setEditOpen}
          institution={institution}
        />
      )}
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
