import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { formatDate } from "@/lib/utils/hebrew";
import { IncidentReportTab } from "@/pages/student/IncidentReportTab";
import { incidentReportApi } from "@/lib/api/endpoints";
import type {
  IncidentReportEntryResponse,
  IncidentReportHistoryResponse,
  UserResponse,
  UserRole,
} from "@/lib/api/types";
import { emptyIncidentFields } from "@/pages/student/incidents/incidentOptions";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  incidentReportApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
    pdfUrl: vi.fn(() => ""),
    combinedPdfUrl: vi.fn(() => ""),
  },
}));

const listMock = vi.mocked(incidentReportApi.list);
const createMock = vi.mocked(incidentReportApi.create);
const updateMock = vi.mocked(incidentReportApi.update);

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

function entry(
  overrides: Partial<IncidentReportEntryResponse>
): IncidentReportEntryResponse {
  return {
    ...emptyIncidentFields("2026-09-08", "מור"),
    event_time: "14:30:00",
    location: "חדר האוכל",
    natures: ["violence", "other"],
    nature_other: "צעקות",
    referrals: ["police"],
    description: "תיאור האירוע של נועה",
    id: "e1",
    student_id: "s1",
    author_id: "u2",
    author_name: "רכזת",
    created_at: "2026-09-08T10:00:00Z",
    updated_at: "2026-09-08T10:00:00Z",
    ...overrides,
  };
}

function history(entries: IncidentReportEntryResponse[]): IncidentReportHistoryResponse {
  return { student_id: "s1", student_name: "נועה", national_id: "123456782", entries };
}

describe("IncidentReportTab", () => {
  beforeEach(() => {
    useAuth.mockReset();
    listMock.mockReset();
    createMock.mockReset();
    updateMock.mockReset();
  });

  it("shows the empty state and the new-report button to an instructor", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(history([]));

    renderWithClient(<IncidentReportTab studentId="s1" />);

    expect(await screen.findByText("לא דווחו אירועים חריגים לחניך.")).toBeInTheDocument();
    expect(screen.getByText("דיווח אירוע חריג חדש")).toBeInTheDocument();
  });

  it("lists reports newest first with the latest expanded", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(
      history([
        entry({ id: "new" }),
        entry({ id: "old", event_date: "2026-01-01", description: "אירוע ישן" }),
      ])
    );

    renderWithClient(<IncidentReportTab studentId="s1" />);

    expect(await screen.findByText("תיאור האירוע של נועה")).toBeInTheDocument();
    expect(screen.getByText("נועה, ת.ז 123456782")).toBeInTheDocument();
    expect(screen.getByText("14:30")).toBeInTheDocument();
    expect(screen.getByText("אלימות · אחר: צעקות")).toBeInTheDocument();
    expect(screen.getByText(formatDate("2026-01-01"))).toBeInTheDocument();
    expect(screen.queryByText("אירוע ישן")).not.toBeInTheDocument();
  });

  it("hides write actions from a professional teacher", async () => {
    signedInAs("professional_teacher");
    listMock.mockResolvedValue(history([entry({})]));

    renderWithClient(<IncidentReportTab studentId="s1" />);

    expect(await screen.findByText("תיאור האירוע של נועה")).toBeInTheDocument();
    expect(screen.queryByText("עריכה")).not.toBeInTheDocument();
    expect(screen.queryByText("מחיקה")).not.toBeInTheDocument();
    expect(screen.queryByText("דיווח אירוע חריג חדש")).not.toBeInTheDocument();
  });

  it("lets an instructor edit but not delete", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(history([entry({})]));

    renderWithClient(<IncidentReportTab studentId="s1" />);

    expect(await screen.findByText("עריכה")).toBeInTheDocument();
    expect(screen.queryByText("מחיקה")).not.toBeInTheDocument();
  });

  it("creates a report with the student auto-filled and the chosen options", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(history([]));
    createMock.mockResolvedValue(entry({ id: "e2" }));

    renderWithClient(<IncidentReportTab studentId="s1" />);

    await userEvent.click(await screen.findByText("דיווח אירוע חריג חדש"));
    expect(screen.getByText("נועה, ת.ז 123456782")).toBeInTheDocument();
    expect(screen.getByLabelText("שם ממלא הטופס")).toHaveValue("מור");
    const save = screen.getByText("שמירת הדו״ח");
    expect(save).toBeDisabled();

    await userEvent.type(screen.getByLabelText("תיאור האירוע"), "נפל בחצר");
    await userEvent.click(screen.getByLabelText("פגיעה ברכוש"));
    await userEvent.click(screen.getByLabelText("משטרה"));
    await userEvent.click(save);

    expect(createMock).toHaveBeenCalledWith(
      "s1",
      expect.objectContaining({
        description: "נפל בחצר",
        natures: ["property_damage"],
        referrals: ["police"],
        event_date: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
      })
    );
  });

  it("edits an existing report", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(history([entry({})]));
    updateMock.mockResolvedValue(entry({}));

    renderWithClient(<IncidentReportTab studentId="s1" />);

    await userEvent.click(await screen.findByText("עריכה"));
    const location = screen.getByLabelText("מקום האירוע");
    await userEvent.clear(location);
    await userEvent.type(location, "חצר");
    await userEvent.click(screen.getByText("שמירה"));

    expect(updateMock).toHaveBeenCalledWith(
      "s1",
      "e1",
      expect.objectContaining({ location: "חצר", natures: ["violence", "other"] })
    );
    expect(updateMock.mock.calls[0][2]).not.toHaveProperty("id");
  });
});
