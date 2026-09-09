import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { PlanForm } from "@/pages/student/program/PlanForm";
import { programApi, programPlansApi, taxonomyApi } from "@/lib/api/endpoints";
import type { LabelTreeNode, ProgramResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  programApi: { get: vi.fn() },
  programPlansApi: { create: vi.fn() },
  taxonomyApi: { tree: vi.fn() },
}));

const getMock = vi.mocked(programApi.get);
const treeMock = vi.mocked(taxonomyApi.tree);
const createMock = vi.mocked(programPlansApi.create);

const program: ProgramResponse = {
  student_id: "s1",
  exists: true,
  entries: [],
  strengths: [],
  areas_to_strengthen: [{ skill_id: "sk1", skill_name: "הקשבה", rating: "yellow" }],
};

const tree: LabelTreeNode[] = [
  {
    id: "l1",
    name: "תקשורת",
    sub_labels: [
      {
        id: "sub1",
        name: "מילולית",
        skills: [
          {
            id: "sk1",
            name: "הקשבה",
            solutions: [{ id: "sol1", text: "ישיבה בקדמת הקבוצה" }],
          },
        ],
      },
    ],
  },
];

describe("PlanForm", () => {
  beforeEach(() => {
    getMock.mockReset();
    treeMock.mockReset();
    createMock.mockReset();
    getMock.mockResolvedValue(program);
    treeMock.mockResolvedValue(tree);
    createMock.mockResolvedValue({
      id: "p1",
      student_id: "s1",
      author_id: "u1",
      created_at: "2026-09-08T00:00:00Z",
      entries: [],
    });
  });

  it("saves the chosen solutions for an area", async () => {
    renderWithClient(<PlanForm studentId="s1" onDone={vi.fn()} />);

    await userEvent.click(await screen.findByLabelText("ישיבה בקדמת הקבוצה"));
    await userEvent.click(screen.getByText("שמירת תוכנית"));

    expect(createMock).toHaveBeenCalledWith("s1", {
      entries: [{ skill_id: "sk1", solution_ids: ["sol1"] }],
    });
  });

  it("blocks saving with no chosen solution", async () => {
    renderWithClient(<PlanForm studentId="s1" onDone={vi.fn()} />);

    await userEvent.click(await screen.findByText("שמירת תוכנית"));

    expect(
      screen.getByText("יש לבחור דרך פתרון אחת לפחות עבור מוקד אחד.")
    ).toBeInTheDocument();
    expect(createMock).not.toHaveBeenCalled();
  });
});
