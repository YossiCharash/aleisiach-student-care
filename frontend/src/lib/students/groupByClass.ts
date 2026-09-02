import type { ClassResponse, StudentResponse } from "@/lib/api/types";

export const UNKNOWN_CLASS_LABEL = "כיתה שהועברה לארכיון";

export interface ClassGroup {
  classId: string;
  className: string;
  students: StudentResponse[];
}

export function groupByClass(
  students: StudentResponse[],
  classes: ClassResponse[]
): ClassGroup[] {
  const namesById = new Map(classes.map((item) => [item.id, item.name]));
  const groups = new Map<string, ClassGroup>();

  for (const student of students) {
    const existing = groups.get(student.class_id);
    if (existing) {
      existing.students.push(student);
      continue;
    }
    groups.set(student.class_id, {
      classId: student.class_id,
      className: namesById.get(student.class_id) ?? UNKNOWN_CLASS_LABEL,
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
    if (first.className === UNKNOWN_CLASS_LABEL) {
      return 1;
    }
    if (second.className === UNKNOWN_CLASS_LABEL) {
      return -1;
    }
    return first.className.localeCompare(second.className, "he");
  });
}
