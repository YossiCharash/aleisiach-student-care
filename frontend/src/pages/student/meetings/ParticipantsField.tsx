import { type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronDown } from "lucide-react";
import { usersApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type { UserResponse, UserRole } from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { toggled } from "@/lib/utils/arrays";
import { Label } from "@/components/ui/Label";
import { Input } from "@/components/ui/Input";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/DropdownMenu";

interface Props {
  id: string;
  value: string;
  onChange: (value: string) => void;
}

const PARTICIPANT_ROLES: readonly UserRole[] = ["manager", "instructor"];

function splitNames(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter((part) => part !== "");
}

function isParticipantCandidate(candidate: UserResponse): boolean {
  return PARTICIPANT_ROLES.includes(candidate.role) && candidate.status !== "disabled";
}

function uniqueByName(members: UserResponse[]): UserResponse[] {
  return members.filter(
    (member, index) =>
      members.findIndex((other) => other.full_name === member.full_name) === index
  );
}

export function ParticipantsField({ id, value, onChange }: Props): ReactNode {
  const { user } = useAuth();
  const isManager = user ? permissions.canManage(user) : false;

  const usersQuery = useQuery({
    queryKey: queryKeys.users,
    queryFn: usersApi.list,
    enabled: isManager,
  });

  const staff: UserResponse[] = uniqueByName(
    (usersQuery.data ?? []).filter(isParticipantCandidate)
  );
  const names: string[] = splitNames(value);
  const selectedCount: number = staff.filter((member) =>
    names.includes(member.full_name)
  ).length;

  return (
    <div className="space-y-2">
      <Label htmlFor={id}>משתתפים</Label>
      {isManager && staff.length > 0 && (
        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              aria-label="בחירת משתתפים מהצוות"
              className="flex min-h-11 w-full items-center justify-between gap-2 rounded-control border border-slate-300 bg-white px-3.5 py-2 text-start text-sm text-ink shadow-soft transition-colors hover:border-slate-400 focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-400/15"
            >
              <span className={selectedCount > 0 ? "" : "text-slate-400"}>
                {selectedCount > 0
                  ? `נבחרו ${selectedCount} מהצוות`
                  : "בחירת משתתפים מהצוות..."}
              </span>
              <ChevronDown className="h-4 w-4 shrink-0 opacity-60" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="max-h-72 w-[var(--radix-dropdown-menu-trigger-width)] overflow-y-auto">
            {staff.map((member) => (
              <DropdownMenuCheckboxItem
                key={member.id}
                checked={names.includes(member.full_name)}
                onSelect={(event) => event.preventDefault()}
                onCheckedChange={(checked) =>
                  onChange(toggled(names, member.full_name, checked === true).join(", "))
                }
              >
                {member.full_name}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
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
