import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import type { StudentDetailsResponse } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { DetailsForm } from "@/pages/student/details/DetailsForm";
import { detailOptionsApi, diagnosesApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  detailOptionsApi: { list: vi.fn() },
  detailsApi: { upsert: vi.fn() },
  diagnosesApi: { list: vi.fn() },
}));

const optionsListMock = vi.mocked(detailOptionsApi.list);
const diagnosesListMock = vi.mocked(diagnosesApi.list);

function details(): StudentDetailsResponse {
  return {
    student_id: "s1",
    national_id: null,
    date_of_birth: null,
    age: null,
    address: null,
    home_language: null,
    idd_severity: null,
    disability_severity: null,
    functioning_level: null,
    additional_diagnoses: [],
    emergency_contacts: [{ full_name: "אמא", relationship: "אמא", phone: "050" }],
    legal_status: null,
    guardians: [],
    has_allergies_or_dietary: false,
    allergies_dietary: [],
    takes_regular_medication: false,
    medications: [],
    medication_independence: null,
    emergency_protocol: null,
    assistive_devices: [],
    assistive_device_other: null,
    expression_mode: null,
    language_comprehension: null,
    previous_institution: null,
    current_institution: null,
    prior_task_experience: null,
    interests_strengths: null,
    triggers: null,
    distress_early_signs: null,
    calming_methods: null,
    sensitive_visible: true,
  };
}

describe("DetailsForm", () => {
  beforeEach(() => {
    optionsListMock.mockReset().mockResolvedValue([]);
    diagnosesListMock.mockReset().mockResolvedValue([]);
  });

  it("renders the disability, functioning and institution fields", () => {
    renderWithClient(<DetailsForm studentId="s1" details={details()} onDone={vi.fn()} />);

    expect(screen.getByText("תיאור המגבלה")).toBeInTheDocument();
    expect(screen.getByText("רמת תפקוד")).toBeInTheDocument();
    expect(screen.getByText("מוסד קודם")).toBeInTheDocument();
    expect(screen.getByText("מוסד נוכחי")).toBeInTheDocument();
  });

  it("offers the contact relationship as a settings-managed datalist, not a fixed list", () => {
    renderWithClient(<DetailsForm studentId="s1" details={details()} onDone={vi.fn()} />);

    const relationship = screen.getAllByPlaceholderText("קרבה")[0];
    expect(relationship).toHaveAttribute("list", "contact-relationship-options");
    expect(relationship.tagName).toBe("INPUT");
  });
});
