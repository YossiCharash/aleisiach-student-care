import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { MeetingsTab } from "@/pages/student/MeetingsTab";
import { meetingsApi } from "@/lib/api/endpoints";
import type { UserResponse, UserRole } from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  meetingsApi: { list: vi.fn(), pdfUrl: vi.fn(() => "") },
}));

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
