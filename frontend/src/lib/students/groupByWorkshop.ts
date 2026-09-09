import type { WorkshopResponse, StudentResponse } from "@/lib/api/types";

export const UNKNOWN_WORKSHOP_LABEL = "סדנה שהועברה לארכיון";
const UNKNOWN_WORKSHOP_COLOR = "#5C5C5C";

export interface WorkshopGroup {
  workshopId: string;
  workshopName: string;
  color: string;
  students: StudentResponse[];
}

export function groupByWorkshop(
  students: StudentResponse[],
  workshops: WorkshopResponse[]
): WorkshopGroup[] {
  const byId = new Map(workshops.map((item) => [item.id, item]));
  const groups = new Map<string, WorkshopGroup>();

  for (const student of students) {
    const existing = groups.get(student.workshop_id);
    if (existing) {
      existing.students.push(student);
      continue;
    }
    const workshop = byId.get(student.workshop_id);
    groups.set(student.workshop_id, {
      workshopId: student.workshop_id,
      workshopName: workshop?.name ?? UNKNOWN_WORKSHOP_LABEL,
      color: workshop?.color ?? UNKNOWN_WORKSHOP_COLOR,
      students: [student],
    });
  }

  const ordered = [...groups.values()];
  for (const group of ordered) {
    group.students.sort((first, second) =>
      first.full_name.localeCompare(second.full_name, "he")
    );
  }
  return ordered.sort((first, second) => {
    if (first.workshopName === UNKNOWN_WORKSHOP_LABEL) {
      return 1;
    }
    if (second.workshopName === UNKNOWN_WORKSHOP_LABEL) {
      return -1;
    }
    return first.workshopName.localeCompare(second.workshopName, "he");
  });
}
