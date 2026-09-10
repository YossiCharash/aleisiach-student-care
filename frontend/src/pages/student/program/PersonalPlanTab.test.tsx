import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { PersonalPlanTab } from "@/pages/student/program/PersonalPlanTab";
import { programPlansApi } from "@/lib/api/endpoints";
import type { PlanResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  programPlansApi: {
    list: vi.fn(),
    pdfUrl: () => "pdf",
    combinedPdfUrl: () => "combined-pdf",
  },
}));

vi.mock("@/pages/student/program/PlanForm", () => ({
  PlanForm: () => <div>טופס תוכנית</div>,
}));

const listMock = vi.mocked(programPlansApi.list);

function plan(id: string, skill: string, solution: string): PlanResponse {
  return {
    id,
    student_id: "s1",
    author_id: "u1",
    created_at: "2026-09-01T10:00:00Z",
    entries: [
      {
        skill_id: `sk-${id}`,
        skill_name_snapshot: skill,
        rating: "yellow",
        solutions: [{ solution_id: `sol-${id}`, solution_text_snapshot: solution }],
      },
    ],
  };
}

describe("PersonalPlanTab", () => {
  beforeEach(() => {
    listMock.mockReset();
  });

  it("shows an empty state and a create button for a manager", async () => {
    listMock.mockResolvedValue([]);

    renderWithClient(<PersonalPlanTab studentId="s1" canWrite />);

    expect(await screen.findByText("אין עדיין תוכנית אישית לחניך.")).toBeInTheDocument();
    expect(screen.getByText("יצירת תוכנית")).toBeInTheDocument();
  });

  it("hides the create button from a read-only user", async () => {
    listMock.mockResolvedValue([]);

    renderWithClient(<PersonalPlanTab studentId="s1" canWrite={false} />);

    expect(await screen.findByText("אין עדיין תוכנית אישית לחניך.")).toBeInTheDocument();
    expect(screen.queryByText("יצירת תוכנית")).not.toBeInTheDocument();
  });

  it("shows the latest plan and reveals history on demand", async () => {
    listMock.mockResolvedValue([
      plan("2", "מוקד חדש", "פתרון חדש"),
      plan("1", "מוקד ישן", "פתרון ישן"),
    ]);

    renderWithClient(<PersonalPlanTab studentId="s1" canWrite />);

    expect(await screen.findByText("מוקד חדש")).toBeInTheDocument();
    expect(screen.queryByText("מוקד ישן")).not.toBeInTheDocument();

    await userEvent.click(screen.getByText("היסטוריה"));

    expect(screen.getByText("מוקד ישן")).toBeInTheDocument();
  });
});
