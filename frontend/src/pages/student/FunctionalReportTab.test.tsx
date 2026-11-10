import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { formatDate } from "@/lib/utils/hebrew";
import { FunctionalReportTab } from "@/pages/student/FunctionalReportTab";
import { functionalReportApi } from "@/lib/api/endpoints";
import type {
  FunctionalReportEntryResponse,
  FunctionalReportHistoryResponse,
  UserResponse,
  UserRole,
} from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  functionalReportApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
    pdfUrl: vi.fn(() => ""),
    combinedPdfUrl: vi.fn(() => ""),
  },
}));

const listMock = vi.mocked(functionalReportApi.list);
const createMock = vi.mocked(functionalReportApi.create);
const updateMock = vi.mocked(functionalReportApi.update);

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

function entry(
  overrides: Partial<FunctionalReportEntryResponse>
): FunctionalReportEntryResponse {
  return {
    id: "e1",
    student_id: "s1",
    report_date: "2026-09-08",
    general_background: "רקע של נועה",
    vocational_domain: "",
    behavioral_emotional_domain: "",
    communication_social_domain: "",
    independence_life_skills_domain: "",
    summary_recommendations: "ממשיכים בתוכנית",
    author_id: "u2",
    author_name: "רכזת",
    created_at: "2026-09-08T10:00:00Z",
    updated_at: "2026-09-08T10:00:00Z",
    ...overrides,
  };
}

function history(
  entries: FunctionalReportEntryResponse[]
): FunctionalReportHistoryResponse {
  return {
    student_id: "s1",
    student_name: "נועה",
    national_id: "123456782",
    date_of_birth: "2010-05-01",
    entries,
  };
}

describe("FunctionalReportTab", () => {
  beforeEach(() => {
    useAuth.mockReset();
    listMock.mockReset();
    createMock.mockReset();
    updateMock.mockReset();
  });

  it("shows the identity and the empty state when no report exists", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(history([]));

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    expect(await screen.findByText("נועה")).toBeInTheDocument();
    expect(screen.getByText("123456782")).toBeInTheDocument();
    expect(screen.getByText("עדיין לא מולא דוח תפקודי לחניך.")).toBeInTheDocument();
    expect(screen.getByText("דוח תפקודי חדש")).toBeInTheDocument();
  });

  it("lists dated reports with the newest one expanded", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(
      history([
        entry({ id: "new", report_date: "2026-09-08" }),
        entry({ id: "old", report_date: "2026-01-01", general_background: "רקע ישן" }),
      ])
    );

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    expect(await screen.findByText("רקע של נועה")).toBeInTheDocument();
    expect(screen.getByText(formatDate("2026-09-08"))).toBeInTheDocument();
    expect(screen.getByText(formatDate("2026-01-01"))).toBeInTheDocument();
    expect(screen.queryByText("רקע ישן")).not.toBeInTheDocument();

    await userEvent.click(screen.getByText("הצגה"));
    expect(screen.getByText("רקע ישן")).toBeInTheDocument();
  });

  it("hides write actions from a read-only professional teacher", async () => {
    signedInAs("professional_teacher");
    listMock.mockResolvedValue(history([entry({})]));

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    expect(await screen.findByText("רקע של נועה")).toBeInTheDocument();
    expect(screen.queryByText("עריכה")).not.toBeInTheDocument();
    expect(screen.queryByText("מחיקה")).not.toBeInTheDocument();
    expect(screen.queryByText("דוח תפקודי חדש")).not.toBeInTheDocument();
  });

  it("lets a manager create a new dated report from an empty form", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(history([entry({})]));
    createMock.mockResolvedValue(entry({ id: "e2" }));

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    await userEvent.click(await screen.findByText("דוח תפקודי חדש"));
    const background = screen.getByLabelText("רקע כללי");
    expect(background).toHaveValue("");
    await userEvent.type(background, "רקע חדש");
    await userEvent.click(screen.getByText("שמירת הדוח"));

    expect(createMock).toHaveBeenCalledWith(
      "s1",
      expect.objectContaining({
        general_background: "רקע חדש",
        report_date: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
      })
    );
  });

  it("lets a manager edit an existing report", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(history([entry({})]));
    updateMock.mockResolvedValue(entry({}));

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    await userEvent.click(await screen.findByText("עריכה"));
    const background = screen.getByLabelText("רקע כללי");
    await userEvent.clear(background);
    await userEvent.type(background, "מעודכן");
    await userEvent.click(screen.getByText("שמירה"));

    expect(updateMock).toHaveBeenCalledWith(
      "s1",
      "e1",
      expect.objectContaining({ general_background: "מעודכן" })
    );
  });
});
