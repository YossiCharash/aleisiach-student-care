import { describe, expect, it, vi, beforeEach } from "vitest";
import { fireEvent, screen, waitFor } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { AddMeetingDialog } from "@/pages/student/meetings/AddMeetingDialog";
import { meetingsApi, programApi, programPlansApi } from "@/lib/api/endpoints";
import type { MeetingResponse, PlanResponse, ProgramResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  programApi: { get: vi.fn() },
  programPlansApi: { list: vi.fn() },
  meetingsApi: { create: vi.fn() },
}));

const program: ProgramResponse = {
  student_id: "s1",
  exists: true,
  entries: [],
  strengths: [{ skill_id: "sk1", skill_name: "הבעה" }],
  areas_to_strengthen: [{ skill_id: "sk2", skill_name: "רחיצת ידיים", rating: "yellow" }],
};

const plan: PlanResponse = {
  id: "p1",
  student_id: "s1",
  author_id: "u1",
  created_at: "2026-08-01T00:00:00Z",
  entries: [
    {
      skill_id: "sk2",
      skill_name_snapshot: "רחיצת ידיים",
      rating: "yellow",
      solutions: [{ solution_id: "so1", solution_text_snapshot: "תרגול יומי" }],
    },
  ],
};

const getMock = vi.mocked(programApi.get);
const listMock = vi.mocked(programPlansApi.list);
const createMock = vi.mocked(meetingsApi.create);

describe("AddMeetingDialog", () => {
  beforeEach(() => {
    getMock.mockReset();
    listMock.mockReset();
    createMock.mockReset();
    getMock.mockResolvedValue(program);
    listMock.mockResolvedValue([plan]);
    createMock.mockResolvedValue({} as MeetingResponse);
  });

  it("previews the current foci and plan and creates a dated meeting with the summary", async () => {
    renderWithClient(<AddMeetingDialog studentId="s1" open onOpenChange={() => {}} />);

    expect(await screen.findByText("הבעה")).toBeInTheDocument();
    expect(screen.getByText("תרגול יומי")).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText("סיכום הישיבה…"), {
      target: { value: "נכתב בישיבה" },
    });
    fireEvent.click(screen.getByText("שמירת ישיבה"));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith(
        "s1",
        expect.objectContaining({ summary: "נכתב בישיבה" })
      )
    );
  });
});
