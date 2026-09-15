import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { SupportedEmploymentTab } from "@/pages/student/SupportedEmploymentTab";
import { supportedEmploymentApi } from "@/lib/api/endpoints";
import type { SupportedEmploymentResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  supportedEmploymentApi: {
    get: vi.fn(),
    upsert: vi.fn(),
    pdfUrl: vi.fn(() => ""),
  },
}));

const getMock = vi.mocked(supportedEmploymentApi.get);
const upsertMock = vi.mocked(supportedEmploymentApi.upsert);

const emptyReport: SupportedEmploymentResponse = {
  student_id: "s1",
  exists: false,
  workplace: "",
  address: "",
  activity_type: "",
  work_process: "",
  work_environment: "",
  required_body_functions: "",
  hazards_and_safety: "",
  workplace_contact: "",
  escort_contact: "",
  mobility: "",
  work_hours: "",
};

const filledReport: SupportedEmploymentResponse = {
  ...emptyReport,
  exists: true,
  workplace: "מאפייה מרכזית",
  hazards_and_safety: "תנור חם",
  work_hours: "08:00-14:00",
};

describe("SupportedEmploymentTab", () => {
  beforeEach(() => {
    getMock.mockReset();
    upsertMock.mockReset();
  });

  it("shows the empty state and a fill button", async () => {
    getMock.mockResolvedValue(emptyReport);

    renderWithClient(<SupportedEmploymentTab studentId="s1" />);

    expect(
      await screen.findByText("עדיין לא מולא ניתוח עבודה נתמכת לחניך.")
    ).toBeInTheDocument();
    expect(screen.getByText("מילוי הטופס")).toBeInTheDocument();
  });

  it("shows the fields when an analysis exists", async () => {
    getMock.mockResolvedValue(filledReport);

    renderWithClient(<SupportedEmploymentTab studentId="s1" />);

    expect(await screen.findByText("מאפייה מרכזית")).toBeInTheDocument();
    expect(screen.getByText("תנור חם")).toBeInTheDocument();
    expect(screen.getByText("08:00-14:00")).toBeInTheDocument();
  });

  it("lets a manager fill and save the analysis", async () => {
    getMock.mockResolvedValue(emptyReport);
    upsertMock.mockResolvedValue({ ...filledReport });

    renderWithClient(<SupportedEmploymentTab studentId="s1" />);

    await userEvent.click(await screen.findByText("מילוי הטופס"));
    await userEvent.type(screen.getByLabelText("מקום העבודה"), "מאפייה");
    await userEvent.click(screen.getByText("שמירה"));

    expect(upsertMock).toHaveBeenCalledWith(
      "s1",
      expect.objectContaining({ workplace: "מאפייה" })
    );
  });
});
