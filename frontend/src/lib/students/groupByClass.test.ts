import { describe, expect, it } from "vitest";
import type { ClassResponse, StudentResponse } from "@/lib/api/types";
import { groupByClass, UNKNOWN_CLASS_LABEL } from "@/lib/students/groupByClass";

function student(id: string, classId: string, fullName: string): StudentResponse {
  return { id, class_id: classId, full_name: fullName, is_archived: false };
}

const classes: ClassResponse[] = [
  { id: "c2", name: "כיתה ב׳" },
  { id: "c1", name: "כיתה א׳" },
];

describe("groupByClass", () => {
  it("groups students under their class and sorts classes by name", () => {
    const groups = groupByClass(
      [student("s1", "c2", "נועה"), student("s2", "c1", "איתי")],
      classes
    );

    expect(groups.map((group) => group.className)).toEqual(["כיתה א׳", "כיתה ב׳"]);
    expect(groups[0].students.map((item) => item.full_name)).toEqual(["איתי"]);
  });

  it("sorts students by name inside each class", () => {
    const groups = groupByClass(
      [
        student("s1", "c1", "תמר"),
        student("s2", "c1", "איתי"),
        student("s3", "c1", "מאיה"),
      ],
      classes
    );

    expect(groups[0].students.map((item) => item.full_name)).toEqual([
      "איתי",
      "מאיה",
      "תמר",
    ]);
  });

  it("keeps students whose class is no longer active under a labelled group", () => {
    const groups = groupByClass(
      [student("s1", "c1", "איתי"), student("s2", "gone", "נועה")],
      classes
    );

    expect(groups.map((group) => group.className)).toEqual([
      "כיתה א׳",
      UNKNOWN_CLASS_LABEL,
    ]);
  });

  it("returns nothing for an empty student list", () => {
    expect(groupByClass([], classes)).toEqual([]);
  });

  it("does not invent groups for classes that have no students", () => {
    const groups = groupByClass([student("s1", "c1", "איתי")], classes);

    expect(groups).toHaveLength(1);
    expect(groups[0].classId).toBe("c1");
  });
});
