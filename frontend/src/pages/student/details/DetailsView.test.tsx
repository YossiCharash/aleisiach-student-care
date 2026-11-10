import { describe, expect, it } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { DetailsView } from "@/pages/student/details/DetailsView";
import type { StudentDetailsResponse } from "@/lib/api/types";

function details(
  overrides: Partial<StudentDetailsResponse> = {}
): StudentDetailsResponse {
  return {
    student_id: "s1",
    national_id: "123456789",
    date_of_birth: "2005-01-01",
    age: 20,
    address: null,
    home_language: null,
    idd_severity: "קלה",
    functioning_level: null,
    additional_diagnoses: [],
    emergency_contacts: [],
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
    prior_task_experience: null,
    interests_strengths: null,
    triggers: null,
    distress_early_signs: null,
    calming_methods: null,
    sensitive_visible: true,
    ...overrides,
  };
}

describe("DetailsView empty handling", () => {
  it("hides empty fields and empty section cards", () => {
    renderWithClient(<DetailsView details={details()} />);

    expect(screen.getByText("אבחונים")).toBeInTheDocument();
    expect(screen.getByText("123456789")).toBeInTheDocument();

    expect(screen.queryByText("כתובת")).not.toBeInTheDocument();
    expect(screen.queryByText(/אוטיזם/)).not.toBeInTheDocument();
    expect(screen.queryByText("אנשי קשר לחירום")).not.toBeInTheDocument();
    expect(screen.queryByText("פרופיל רפואי ובטיחותי קריטי")).not.toBeInTheDocument();
    expect(screen.queryByText("ערוץ תקשורת מועדף")).not.toBeInTheDocument();
    expect(screen.queryByText("רקע חינוכי ותעסוקתי קודם")).not.toBeInTheDocument();
    expect(screen.queryByText("תעודת זהות רגשית")).not.toBeInTheDocument();
    expect(screen.queryByText("אפוטרופסות ומעמד משפטי")).not.toBeInTheDocument();
    expect(screen.queryByText("—")).not.toBeInTheDocument();
  });

  it("shows sections and values that are filled", () => {
    renderWithClient(
      <DetailsView
        details={details({
          functioning_level: "בינוני",
          expression_mode: "דיבור מילולי שוטף",
          previous_institution: "גן תקשורת",
          interests_strengths: "ציור",
          emergency_contacts: [{ full_name: "אמא", relationship: "אם", phone: "050" }],
        })}
      />
    );

    expect(screen.getByText("ערוץ תקשורת מועדף")).toBeInTheDocument();
    expect(screen.getByText("דיבור מילולי שוטף")).toBeInTheDocument();
    expect(screen.getByText("רקע חינוכי ותעסוקתי קודם")).toBeInTheDocument();
    expect(screen.getByText("גן תקשורת")).toBeInTheDocument();
    expect(screen.getByText("תעודת זהות רגשית")).toBeInTheDocument();
    expect(screen.getByText("אנשי קשר לחירום")).toBeInTheDocument();
    expect(screen.getByText("אמא")).toBeInTheDocument();
  });
});
