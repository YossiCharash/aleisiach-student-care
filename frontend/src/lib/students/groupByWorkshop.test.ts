import { describe, expect, it } from "vitest";
import type { WorkshopResponse, StudentResponse } from "@/lib/api/types";
import { groupByWorkshop, UNKNOWN_WORKSHOP_LABEL } from "@/lib/students/groupByWorkshop";

function student(id: string, workshopId: string, fullName: string): StudentResponse {
  return { id, workshop_id: workshopId, full_name: fullName, is_archived: false };
}

function workshop(id: string, name: string, color: string): WorkshopResponse {
  return { id, name, color, instructor_id: null, instructor_name: null };
}

const workshops: WorkshopResponse[] = [
  workshop("c2", "סדנה ב׳", "#85C441"),
  workshop("c1", "סדנה א׳", "#3F8420"),
];

describe("groupByWorkshop", () => {
  it("groups students under their class and sorts workshops by name", () => {
    const groups = groupByWorkshop(
      [student("s1", "c2", "נועה"), student("s2", "c1", "איתי")],
      workshops
    );

    expect(groups.map((group) => group.workshopName)).toEqual(["סדנה א׳", "סדנה ב׳"]);
    expect(groups[0].students.map((item) => item.full_name)).toEqual(["איתי"]);
  });

  it("sorts students by name inside each class", () => {
    const groups = groupByWorkshop(
      [
        student("s1", "c1", "תמר"),
        student("s2", "c1", "איתי"),
        student("s3", "c1", "מאיה"),
      ],
      workshops
    );

    expect(groups[0].students.map((item) => item.full_name)).toEqual([
      "איתי",
      "מאיה",
      "תמר",
    ]);
  });

  it("keeps students whose class is no longer active under a labelled group", () => {
    const groups = groupByWorkshop(
      [student("s1", "c1", "איתי"), student("s2", "gone", "נועה")],
      workshops
    );

    expect(groups.map((group) => group.workshopName)).toEqual([
      "סדנה א׳",
      UNKNOWN_WORKSHOP_LABEL,
    ]);
  });

  it("returns nothing for an empty student list", () => {
    expect(groupByWorkshop([], workshops)).toEqual([]);
  });

  it("does not invent groups for workshops that have no students", () => {
    const groups = groupByWorkshop([student("s1", "c1", "איתי")], workshops);

    expect(groups).toHaveLength(1);
    expect(groups[0].workshopId).toBe("c1");
  });
});
