import type { StaffMember } from "@/lib/api/types";

export function withAssigned(
  candidates: StaffMember[],
  assigned: StaffMember[]
): StaffMember[] {
  const known = new Set(candidates.map((member) => member.id));
  const missing = assigned.filter(
    (member, index) =>
      !known.has(member.id) &&
      assigned.findIndex((other) => other.id === member.id) === index
  );
  return [...candidates, ...missing];
}
