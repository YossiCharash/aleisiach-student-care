import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { MedicalSummaryTab } from "@/pages/student/MedicalSummaryTab";
import { medicalSummaryApi } from "@/lib/api/endpoints";
import type { MedicalSummaryResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  medicalSummaryApi: {
    get: vi.fn(),
    upsert: vi.fn(),
    pdfUrl: vi.fn(() => ""),
  },
}));

const getMock = vi.mocked(medicalSummaryApi.get);
const upsertMock = vi.mocked(medicalSummaryApi.upsert);

const emptySummary: MedicalSummaryResponse = {
  student_id: "s1",
  exists: false,
  student_name: "נועה כהן",
  national_id: "123456782",
  date_of_birth: "2000-05-01",
  address: "רחוב הגפן 3",
  written_by_name: null,
  updated_at: null,
  phone: "",
  lives_with: [],
  allergies: "",
  known_syndrome: "",
  background_diseases: "",
  hospitalizations_surgeries: "",
  dental_treatment: [],
  dentures: [],
  epilepsy_known: null,
  epilepsy_seizure_nature: "",
  epilepsy_seizure_frequency: "",
  epilepsy_last_seizure: null,
  epilepsy_seizure_treatment: "",
  dual_diagnosis_known: null,
  dual_diagnosis_expression: "",
  dual_diagnosis_frequency: "",
  dual_diagnosis_treatment: "",
  skin_integrity: [],
  skin_known_issues: "",
  comprehension: [],
  communication: [],
  communication_other: "",
  speech: [],
  vision: [],
  hearing: [],
  functioning: [],
  mobility: [],
  eating: [],
  gastrostomy_feeding: null,
  formula: "",
  chewing_swallowing: [],
  food_texture: [],
  diet: [],
  diet_other: "",
  continence: [],
  loves: "",
  calming: "",
  angering: "",
  frightening: "",
  stress_behavior: "",
  care_recommendations: "",
  general_notes: "",
  guardian_name: "",
  guardian_relation: "",
  guardian_phone: "",
  health_fund: "",
  supplemental_insurance: null,
  supplemental_insurance_detail: "",
  attending_doctor: "",
  care_nurse: "",
  community_social_worker: "",
  social_worker_phone: "",
  filler_role: "",
};

const filledSummary: MedicalSummaryResponse = {
  ...emptySummary,
  exists: true,
  allergies: "בוטנים",
  mobility: ["escort", "aids"],
  diet: ["other"],
  diet_other: "ללא גלוטן",
  epilepsy_known: false,
  written_by_name: "מנהלת",
  updated_at: "2026-11-10T10:00:00Z",
};

describe("MedicalSummaryTab", () => {
  beforeEach(() => {
    getMock.mockReset();
    upsertMock.mockReset();
  });

  it("shows the auto-filled identity and the empty state", async () => {
    getMock.mockResolvedValue(emptySummary);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    expect(
      await screen.findByText("עדיין לא מולא סיכום מידע רפואי לחניך.")
    ).toBeInTheDocument();
    expect(screen.getByText("נועה כהן")).toBeInTheDocument();
    expect(screen.getByText("123456782")).toBeInTheDocument();
    expect(screen.getByText("רחוב הגפן 3")).toBeInTheDocument();
  });

  it("shows the chosen options and texts when a summary exists", async () => {
    getMock.mockResolvedValue(filledSummary);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    expect(await screen.findByText("בוטנים")).toBeInTheDocument();
    expect(
      screen.getByText("זקוק לליווי · משתמש בעזרים (הליכון, כסא גלגלים, קביים)")
    ).toBeInTheDocument();
    expect(screen.getByText("אחר: ללא גלוטן")).toBeInTheDocument();
    expect(screen.getByText("לא")).toBeInTheDocument();
  });

  it("lets a manager tick options, type text and save", async () => {
    getMock.mockResolvedValue(emptySummary);
    upsertMock.mockResolvedValue(filledSummary);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    await userEvent.click(await screen.findByText("מילוי הטופס"));
    await userEvent.type(screen.getByLabelText("רגישויות / אלרגיה ידועה"), "בוטנים");
    await userEvent.click(screen.getByLabelText("זקוק לליווי"));
    await userEvent.click(screen.getByLabelText("מתבטא במילים בודדות"));
    await userEvent.click(screen.getByText("שמירה"));

    expect(upsertMock).toHaveBeenCalledTimes(1);
    const [studentId, body] = upsertMock.mock.calls[0];
    expect(studentId).toBe("s1");
    expect(body.allergies).toBe("בוטנים");
    expect(body.mobility).toEqual(["escort"]);
    expect(body.communication).toEqual(["single_words"]);
    expect(body).not.toHaveProperty("student_name");
    expect(await screen.findByText("בוטנים")).toBeInTheDocument();
  });
});
