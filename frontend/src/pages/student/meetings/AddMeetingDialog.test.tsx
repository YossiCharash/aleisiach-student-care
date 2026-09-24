import { describe, expect, it, vi, beforeEach } from "vitest";
import { fireEvent, screen, waitFor } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { AddMeetingDialog } from "@/pages/student/meetings/AddMeetingDialog";
import { meetingsApi, programPlansApi } from "@/lib/api/endpoints";
import type { MeetingResponse, PlanResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  programPlansApi: { list: vi.fn() },
  meetingsApi: { create: vi.fn(), list: vi.fn() },
  usersApi: { list: vi.fn().mockResolvedValue([]) },
}));

vi.mock("@/lib/auth/AuthContext", () => ({
  useAuth: () => ({ user: { id: "u1", full_name: "מור", role: "manager" } }),
}));

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

const previousMeeting: MeetingResponse = {
  id: "m0",
  student_id: "s1",
  author_id: "u1",
  meeting_date: "2026-07-01",
  participants: "דנה",
  summary: "סיכום קודם",
  created_at: "2026-07-01T00:00:00Z",
  updated_at: "2026-07-01T00:00:00Z",
  strengths: [{ skill_id: "sk1", skill_name: "הבעה" }],
  areas_to_strengthen: [{ skill_id: "sk2", skill_name: "רחיצת ידיים", rating: "yellow" }],
  plan_entries: [
    {
      skill_id: "sk2",
      skill_name_snapshot: "רחיצת ידיים",
      rating: "yellow",
      solutions: [{ solution_id: "so0", solution_text_snapshot: "תרגול מהעבר" }],
    },
  ],
};

const listMock = vi.mocked(programPlansApi.list);
const meetingsListMock = vi.mocked(meetingsApi.list);
const createMock = vi.mocked(meetingsApi.create);

describe("AddMeetingDialog", () => {
  beforeEach(() => {
    listMock.mockReset();
    meetingsListMock.mockReset();
    createMock.mockReset();
    listMock.mockResolvedValue([plan]);
    meetingsListMock.mockResolvedValue([]);
    createMock.mockResolvedValue({} as MeetingResponse);
  });

  it("previews only the personal plan (no foci) and creates a dated meeting", async () => {
    renderWithClient(<AddMeetingDialog studentId="s1" open onOpenChange={() => {}} />);

    expect(await screen.findByText("תוכנית אישית")).toBeInTheDocument();
    expect(screen.getByText("תרגול יומי")).toBeInTheDocument();
    expect(screen.queryByText("מוקדים לחיזוק")).not.toBeInTheDocument();
    expect(screen.queryByText("מוקדי כוח")).not.toBeInTheDocument();

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

  it("shows the previous meeting summary and plan for reference", async () => {
    meetingsListMock.mockResolvedValue([previousMeeting]);
    renderWithClient(<AddMeetingDialog studentId="s1" open onOpenChange={() => {}} />);

    expect(await screen.findByText(/^הישיבה הקודמת/)).toBeInTheDocument();
    expect(screen.getByText("סיכום קודם")).toBeInTheDocument();
    expect(screen.getByText("תרגול מהעבר")).toBeInTheDocument();
  });
});
