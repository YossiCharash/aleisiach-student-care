import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { FunctionalReportTab } from "@/pages/student/FunctionalReportTab";
import { functionalReportApi } from "@/lib/api/endpoints";
import type { FunctionalReportResponse, UserResponse, UserRole } from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  functionalReportApi: {
    get: vi.fn(),
    upsert: vi.fn(),
    pdfUrl: vi.fn(() => ""),
  },
}));

const getMock = vi.mocked(functionalReportApi.get);
const upsertMock = vi.mocked(functionalReportApi.upsert);

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

const emptyReport: FunctionalReportResponse = {
  student_id: "s1",
  exists: false,
  student_name: "נועה",
  national_id: "123456782",
  date_of_birth: "2010-05-01",
  general_background: "",
  vocational_domain: "",
  behavioral_emotional_domain: "",
  communication_social_domain: "",
  independence_life_skills_domain: "",
  summary_recommendations: "",
  written_by_name: null,
  updated_at: null,
};

const filledReport: FunctionalReportResponse = {
  ...emptyReport,
  exists: true,
  general_background: "רקע של נועה",
  summary_recommendations: "ממשיכים בתוכנית",
  written_by_name: "רכזת",
  updated_at: "2026-09-08T10:00:00Z",
};

describe("FunctionalReportTab", () => {
  beforeEach(() => {
    useAuth.mockReset();
    getMock.mockReset();
    upsertMock.mockReset();
  });

  it("auto-fills identity from the student and shows the empty state", async () => {
    signedInAs("manager");
    getMock.mockResolvedValue(emptyReport);

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    expect(await screen.findByText("נועה")).toBeInTheDocument();
    expect(screen.getByText("123456782")).toBeInTheDocument();
    expect(screen.getByText("עדיין לא מולא דוח תפקודי לתלמיד.")).toBeInTheDocument();
    expect(screen.getByText("מילוי הדוח")).toBeInTheDocument();
  });

  it("shows the report sections and issuer when a report exists", async () => {
    signedInAs("instructor");
    getMock.mockResolvedValue(filledReport);

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    expect(await screen.findByText("רקע של נועה")).toBeInTheDocument();
    expect(screen.getByText("ממשיכים בתוכנית")).toBeInTheDocument();
    expect(screen.getByText("נכתב על ידי: רכזת")).toBeInTheDocument();
  });

  it("hides the edit button from a read-only professional teacher", async () => {
    signedInAs("professional_teacher");
    getMock.mockResolvedValue(filledReport);

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    expect(await screen.findByText("רקע של נועה")).toBeInTheDocument();
    expect(screen.queryByText("עריכה")).not.toBeInTheDocument();
    expect(screen.queryByText("מילוי הדוח")).not.toBeInTheDocument();
  });

  it("lets a manager edit and save the report", async () => {
    signedInAs("manager");
    getMock.mockResolvedValue(emptyReport);
    upsertMock.mockResolvedValue({ ...filledReport });

    renderWithClient(<FunctionalReportTab studentId="s1" />);

    await userEvent.click(await screen.findByText("מילוי הדוח"));
    const editor = await screen.findAllByRole("textbox");
    await userEvent.type(editor[0], "רקע חדש");
    await userEvent.click(screen.getByText("שמירה"));

    expect(upsertMock).toHaveBeenCalledWith(
      "s1",
      expect.objectContaining({ general_background: "רקע חדש" })
    );
  });
});
