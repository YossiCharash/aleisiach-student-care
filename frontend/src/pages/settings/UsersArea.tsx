import { useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { UserPlus } from "lucide-react";
import { usersApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { UserResponse } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { roleLabels, userStatusLabels } from "@/lib/utils/hebrew";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { InviteUserDialog } from "@/pages/settings/InviteUserDialog";

export function UsersArea(): ReactNode {
  const [inviteOpen, setInviteOpen] = useState(false);
  const query = useQuery({ queryKey: queryKeys.users, queryFn: usersApi.list });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-ink">משתמשים</h2>
        <Button onClick={() => setInviteOpen(true)}>
          <UserPlus className="h-4 w-4" />
          הזמנת משתמש
        </Button>
      </div>

      {query.isLoading && <LoadingState />}
      {query.isError && <ErrorState error={query.error} />}
      {query.data && <UsersTable users={query.data} />}

      <InviteUserDialog open={inviteOpen} onOpenChange={setInviteOpen} />
    </div>
  );
}

function UsersTable({ users }: { users: UserResponse[] }): ReactNode {
  if (users.length === 0) {
    return <EmptyState>אין משתמשים.</EmptyState>;
  }

  return (
    <Card>
      <CardContent className="p-0">
        <table className="w-full text-start text-sm">
          <thead className="border-b border-slate-100 text-ink-muted">
            <tr>
              <th className="px-4 py-3 text-start font-medium">שם</th>
              <th className="px-4 py-3 text-start font-medium">דוא״ל</th>
              <th className="px-4 py-3 text-start font-medium">תפקיד</th>
              <th className="px-4 py-3 text-start font-medium">סטטוס</th>
              <th className="px-4 py-3 text-start font-medium">פעולות</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <UserRow key={user.id} user={user} />
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

const statusTone = {
  active: "green",
  invited: "yellow",
  disabled: "neutral",
} as const;

function UserRow({ user }: { user: UserResponse }): ReactNode {
  const queryClient = useQueryClient();
  const { user: currentUser } = useAuth();
  const isSelf = currentUser?.id === user.id;

  const mutation = useMutation({
    mutationFn: () =>
      user.status === "disabled" ? usersApi.enable(user.id) : usersApi.disable(user.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.users }),
  });

  return (
    <tr className="border-b border-slate-50 last:border-0">
      <td className="px-4 py-3 font-medium text-ink">{user.full_name}</td>
      <td className="px-4 py-3 text-ink-muted">{user.email}</td>
      <td className="px-4 py-3 text-ink-muted">{roleLabels[user.role]}</td>
      <td className="px-4 py-3">
        <Badge tone={statusTone[user.status]}>{userStatusLabels[user.status]}</Badge>
      </td>
      <td className="px-4 py-3">
        {!isSelf && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
          >
            {user.status === "disabled" ? "הפעלה" : "השבתה"}
          </Button>
        )}
      </td>
    </tr>
  );
}
