import { describe, expect, it, vi, beforeEach } from "vitest";
import { fireEvent, screen, waitFor } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { SocialNoteTab } from "@/pages/student/SocialNoteTab";
import { socialNoteApi } from "@/lib/api/endpoints";
import type {
  SocialNoteEntryResponse,
  SocialNoteReportResponse,
  UserResponse,
  UserRole,
} from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  socialNoteApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
    pdfUrl: vi.fn(() => ""),
    combinedPdfUrl: vi.fn(() => ""),
  },
}));

const listMock = vi.mocked(socialNoteApi.list);
const createMock = vi.mocked(socialNoteApi.create);
const updateMock = vi.mocked(socialNoteApi.update);
const archiveMock = vi.mocked(socialNoteApi.archive);

function entry(
  overrides: Partial<SocialNoteEntryResponse> = {}
): SocialNoteEntryResponse {
  return {
    id: "n1",
    student_id: "s1",
    note_date: "2026-08-30",
    content: "שיחה עם ההורים",
    author_id: "u1",
    author_name: "מור",
    created_at: "2026-08-30T00:00:00Z",
    updated_at: "2026-08-30T00:00:00Z",
    ...overrides,
  };
}

function report(entries: SocialNoteEntryResponse[]): SocialNoteReportResponse {
  return { student_id: "s1", student_name: "דנה", entries };
}

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

describe("SocialNoteTab", () => {
  beforeEach(() => {
    useAuth.mockReset();
    listMock.mockReset();
    createMock.mockReset();
    updateMock.mockReset();
    archiveMock.mockReset();
  });

  it("shows an empty state and a new-note button for a manager", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(report([]));

    renderWithClient(<SocialNoteTab studentId="s1" />);

    expect(await screen.findByText("אין סיכומי עו״ס עדיין.")).toBeInTheDocument();
    expect(screen.getByText("הערה חדשה")).toBeInTheDocument();
  });

  it("renders a dated entry with its author for a read-only instructor", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(report([entry()]));

    renderWithClient(<SocialNoteTab studentId="s1" />);

    expect(await screen.findByText("שיחה עם ההורים")).toBeInTheDocument();
    expect(screen.getByText(/מור/)).toBeInTheDocument();
    expect(screen.queryByText("הערה חדשה")).not.toBeInTheDocument();
    expect(screen.queryByText("עריכה")).not.toBeInTheDocument();
  });

  it("lets a manager add a dated note", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(report([]));
    createMock.mockResolvedValue(entry());

    renderWithClient(<SocialNoteTab studentId="s1" />);

    fireEvent.click(await screen.findByText("הערה חדשה"));
    fireEvent.change(screen.getByLabelText("הערה"), {
      target: { value: "הערה חדשה מהעו״ס" },
    });
    fireEvent.click(screen.getByText("שמירת הערה"));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith("s1", {
        note_date: expect.any(String),
        content: "הערה חדשה מהעו״ס",
      })
    );
  });

  it("lets a manager edit an entry's content", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(report([entry()]));
    updateMock.mockResolvedValue(entry({ content: "מעודכן" }));

    renderWithClient(<SocialNoteTab studentId="s1" />);

    fireEvent.click(await screen.findByText("עריכה"));
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "מעודכן" } });
    fireEvent.click(screen.getByText("שמירה"));

    await waitFor(() =>
      expect(updateMock).toHaveBeenCalledWith("s1", "n1", { content: "מעודכן" })
    );
  });

  it("lets a manager archive an entry after confirmation", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(report([entry()]));
    archiveMock.mockResolvedValue(entry());

    renderWithClient(<SocialNoteTab studentId="s1" />);

    fireEvent.click(await screen.findByText("מחיקה"));
    fireEvent.click(await screen.findByText("כן, למחוק"));

    await waitFor(() => expect(archiveMock).toHaveBeenCalledWith("s1", "n1"));
  });
});
