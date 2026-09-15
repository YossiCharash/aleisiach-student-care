import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { ReceptionReportTab } from "@/pages/student/ReceptionReportTab";
import { receptionReportApi } from "@/lib/api/endpoints";
import type { ReceptionChecklistItem, ReceptionReportResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  receptionReportApi: {
    get: vi.fn(),
    upsert: vi.fn(),
    pdfUrl: vi.fn(() => ""),
  },
}));

const getMock = vi.mocked(receptionReportApi.get);
const upsertMock = vi.mocked(receptionReportApi.upsert);

const off: ReceptionChecklistItem = { done: false, note: "" };

const emptyReport: ReceptionReportResponse = {
  student_id: "s1",
  exists: false,
  student_name: "נועה",
  national_id: "123456782",
  date_of_birth: "2010-05-01",
  committee_date: null,
  committee_participants: "",
  intake_date: null,
  committee_summary: "",
  committee_recommendations: "",
  framework_code: "",
  tariff_code: "",
  committee_held: off,
  director_approval: off,
  family_guardian_housing_updated: off,
  community_social_worker_updated: off,
  management_updated: off,
  written_by_name: null,
  updated_at: null,
};

const filledReport: ReceptionReportResponse = {
  ...emptyReport,
  exists: true,
  committee_summary: "סיכום הוועדה",
  framework_code: "1234",
  committee_held: { done: true, note: "נערכה כנדרש" },
  written_by_name: "רכזת",
  updated_at: "2026-09-15T10:00:00Z",
};

describe("ReceptionReportTab", () => {
  beforeEach(() => {
    getMock.mockReset();
    upsertMock.mockReset();
  });

  it("auto-fills identity and shows the empty state", async () => {
    getMock.mockResolvedValue(emptyReport);

    renderWithClient(<ReceptionReportTab studentId="s1" />);

    expect(await screen.findByText("נועה")).toBeInTheDocument();
    expect(screen.getByText("123456782")).toBeInTheDocument();
    expect(screen.getByText("עדיין לא מולא דוח קבלה לחניך.")).toBeInTheDocument();
    expect(screen.getByText("מילוי הדוח")).toBeInTheDocument();
  });

  it("shows the details, checklist and issuer when a report exists", async () => {
    getMock.mockResolvedValue(filledReport);

    renderWithClient(<ReceptionReportTab studentId="s1" />);

    expect(await screen.findByText("סיכום הוועדה")).toBeInTheDocument();
    expect(screen.getByText("1234")).toBeInTheDocument();
    expect(screen.getByText("— נערכה כנדרש")).toBeInTheDocument();
    expect(screen.getByText("נכתב על ידי: רכזת")).toBeInTheDocument();
  });

  it("lets a manager fill and save the report", async () => {
    getMock.mockResolvedValue(emptyReport);
    upsertMock.mockResolvedValue({ ...filledReport });

    renderWithClient(<ReceptionReportTab studentId="s1" />);

    await userEvent.click(await screen.findByText("מילוי הדוח"));
    await userEvent.type(screen.getByLabelText("סיכום ועדת קבלה"), "סיכום חדש");
    await userEvent.click(screen.getByLabelText("התקיימה ועדת קבלה על פי הנוהל?"));
    await userEvent.click(screen.getByText("שמירה"));

    expect(upsertMock).toHaveBeenCalledWith(
      "s1",
      expect.objectContaining({
        committee_summary: "סיכום חדש",
        committee_held: expect.objectContaining({ done: true }),
      })
    );
  });
});
