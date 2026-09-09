import { describe, expect, it, vi, beforeEach } from "vitest";
import { fireEvent, screen, waitFor } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { MeetingsTab } from "@/pages/student/MeetingsTab";
import { meetingsApi } from "@/lib/api/endpoints";
import type { MeetingResponse, UserResponse, UserRole } from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  meetingsApi: {
    list: vi.fn(),
    pdfUrl: vi.fn(() => ""),
    updateSummary: vi.fn(),
  },
}));

const meeting: MeetingResponse = {
  id: "m1",
  student_id: "s1",
  author_id: "u1",
  meeting_date: "2026-08-15",
  summary: "סיכום קיים",
  created_at: "2026-08-15T00:00:00Z",
  updated_at: "2026-08-15T00:00:00Z",
  strengths: [{ skill_id: "sk1", skill_name: "הבעה" }],
  areas_to_strengthen: [{ skill_id: "sk2", skill_name: "רחיצת ידיים", rating: "yellow" }],
  plan_entries: [
    {
      skill_id: "sk2",
      skill_name_snapshot: "רחיצת ידיים",
      rating: "yellow",
      solutions: [{ solution_id: "so1", solution_text_snapshot: "תרגול יומי" }],
    },
  ],
};

const updateMock = vi.mocked(meetingsApi.updateSummary);

vi.mock("@/pages/student/meetings/AddMeetingDialog", () => ({
  AddMeetingDialog: ({ open }: { open: boolean }) =>
    open ? <div>דיאלוג ישיבה חדשה</div> : null,
}));

const listMock = vi.mocked(meetingsApi.list);

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

function renderTab(props: {
  autoOpenNew?: boolean;
  onAutoOpenConsumed?: () => void;
}): void {
  renderWithClient(<MeetingsTab studentId="s1" {...props} />);
}

describe("MeetingsTab auto-open", () => {
  beforeEach(() => {
    useAuth.mockReset();
    listMock.mockReset();
    listMock.mockResolvedValue([]);
  });

  it("auto-opens the new-meeting dialog for a writer and reports consumption", async () => {
    signedInAs("manager");
    const onConsumed = vi.fn();
    renderTab({ autoOpenNew: true, onAutoOpenConsumed: onConsumed });

    expect(await screen.findByText("דיאלוג ישיבה חדשה")).toBeInTheDocument();
    expect(onConsumed).toHaveBeenCalledOnce();
  });

  it("does not auto-open for a read-only professional teacher", async () => {
    signedInAs("professional_teacher");
    const onConsumed = vi.fn();
    renderTab({ autoOpenNew: true, onAutoOpenConsumed: onConsumed });

    expect(await screen.findByText("ישיבות צוות")).toBeInTheDocument();
    expect(screen.queryByText("דיאלוג ישיבה חדשה")).not.toBeInTheDocument();
    expect(onConsumed).not.toHaveBeenCalled();
  });

  it("does not open the dialog when autoOpenNew is false", async () => {
    signedInAs("manager");
    renderTab({ autoOpenNew: false });

    expect(await screen.findByText("ישיבות צוות")).toBeInTheDocument();
    expect(screen.queryByText("דיאלוג ישיבה חדשה")).not.toBeInTheDocument();
  });
});

describe("MeetingsTab history", () => {
  beforeEach(() => {
    useAuth.mockReset();
    listMock.mockReset();
    updateMock.mockReset();
    listMock.mockResolvedValue([meeting]);
    updateMock.mockResolvedValue(meeting);
  });

  it("renders the dated snapshot of foci, plan and the summary", async () => {
    signedInAs("professional_teacher");
    renderTab({});

    expect(await screen.findByText(/2026/)).toBeInTheDocument();
    expect(screen.getByText("הבעה")).toBeInTheDocument();
    expect(screen.getByText("תרגול יומי")).toBeInTheDocument();
    expect(screen.getByText("סיכום קיים")).toBeInTheDocument();
  });

  it("hides the edit-summary control from a read-only professional teacher", async () => {
    signedInAs("professional_teacher");
    renderTab({});

    await screen.findByText("סיכום קיים");
    expect(screen.queryByText("עריכת סיכום")).not.toBeInTheDocument();
  });

  it("lets a writer edit and save the summary", async () => {
    signedInAs("manager");
    renderTab({});

    fireEvent.click(await screen.findByText("עריכת סיכום"));
    const textarea = screen.getByRole("textbox");
    fireEvent.change(textarea, { target: { value: "סיכום מעודכן" } });
    fireEvent.click(screen.getByText("שמירה"));

    await waitFor(() =>
      expect(updateMock).toHaveBeenCalledWith("s1", "m1", { summary: "סיכום מעודכן" })
    );
  });
});
