import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { ProgramForm } from "@/pages/student/program/ProgramForm";
import { programApi } from "@/lib/api/endpoints";
import type { ProgramResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  programApi: { upsert: vi.fn() },
}));

vi.mock("@/components/SkillRatingTree", () => ({
  SkillRatingTree: () => <div>עץ טקסונומיה</div>,
}));

const upsertMock = vi.mocked(programApi.upsert);

const emptyProgram: ProgramResponse = {
  student_id: "s1",
  exists: false,
  entries: [],
  strengths: [],
  areas_to_strengthen: [],
};

const filledProgram: ProgramResponse = {
  student_id: "s1",
  exists: true,
  entries: [
    {
      skill_id: "sk1",
      skill_name_snapshot: "רחיצת ידיים",
      rating: "yellow",
      solutions: [{ solution_id: "sol1", solution_text_snapshot: "תרגול יומי" }],
    },
  ],
  strengths: [],
  areas_to_strengthen: [],
};

describe("ProgramForm", () => {
  beforeEach(() => {
    upsertMock.mockReset();
    upsertMock.mockResolvedValue(filledProgram);
  });

  it("prefills the draft count from the existing program", () => {
    renderWithClient(
      <ProgramForm studentId="s1" program={filledProgram} onDone={vi.fn()} />
    );

    expect(screen.getByText("1 כישורים דורגו")).toBeInTheDocument();
  });

  it("submits the prefilled entries on save", async () => {
    renderWithClient(
      <ProgramForm studentId="s1" program={filledProgram} onDone={vi.fn()} />
    );

    await userEvent.click(screen.getByText("שמירת תוכנית"));

    expect(upsertMock).toHaveBeenCalledWith("s1", {
      entries: [{ skill_id: "sk1", rating: "yellow", solution_ids: ["sol1"] }],
    });
  });

  it("blocks an empty program and does not call the API", async () => {
    renderWithClient(
      <ProgramForm studentId="s1" program={emptyProgram} onDone={vi.fn()} />
    );

    await userEvent.click(screen.getByText("שמירת תוכנית"));

    expect(screen.getByText("יש לדרג לפחות כישור אחד.")).toBeInTheDocument();
    expect(upsertMock).not.toHaveBeenCalled();
  });
});
