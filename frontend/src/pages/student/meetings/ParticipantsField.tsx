import { type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";

interface Props {
  id: string;
  value: string;
  onChange: (value: string) => void;
}

function appendName(current: string, name: string): string {
  const parts = current
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part !== "");
  if (parts.includes(name)) {
    return current;
  }
  return [...parts, name].join(", ");
}

export function ParticipantsField({ id, value, onChange }: Props): ReactNode {
  const { user } = useAuth();
  const isManager = user ? permissions.canManage(user) : false;

  const usersQuery = useQuery({
    queryKey: queryKeys.users,
    queryFn: usersApi.list,
    enabled: isManager,
  });

  const instructors = (usersQuery.data ?? []).filter(
    (candidate) => candidate.role === "instructor" && candidate.status !== "disabled"
  );

  return (
    <div className="space-y-2">
      <Label htmlFor={id}>משתתפים</Label>
      {isManager && instructors.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {instructors.map((instructor) => (
            <button
              key={instructor.id}
              type="button"
              onClick={() => onChange(appendName(value, instructor.full_name))}
              className="rounded-full border border-slate-200 bg-white px-3 py-1 text-sm text-ink-muted transition-colors hover:border-brand-300 hover:text-ink"
            >
              {instructor.full_name}
            </button>
          ))}
        </div>
      )}
      <Input
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="שמות המשתתפים, מופרדים בפסיק…"
      />
    </div>
  );
}
