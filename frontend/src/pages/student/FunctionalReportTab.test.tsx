import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { FunctionalReportTab } from "@/pages/student/FunctionalReportTab";
import { detailsApi } from "@/lib/api/endpoints";
import type { StudentDetailsResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  detailsApi: { get: vi.fn() },
}));

const getMock = vi.mocked(detailsApi.get);

const details = {
  expression_mode: "דיבור",
  language_comprehension: "מלאה",
  interests_strengths: "מוזיקה",
  triggers: "רעש",
  distress_early_signs: "מתיחות",
  calming_methods: "הפסקה",
} as unknown as StudentDetailsResponse;

describe("FunctionalReportTab", () => {
  beforeEach(() => {
    getMock.mockReset();
    getMock.mockResolvedValue(details);
  });

  it("renders the emotional-profile and communication-channel summary", async () => {
    renderWithClient(<FunctionalReportTab studentId="s1" />);

    expect(await screen.findByText("תעודת זהות רגשית")).toBeInTheDocument();
    expect(screen.getByText("ערוץ תקשורת מועדף")).toBeInTheDocument();
    expect(screen.getByText("מוזיקה")).toBeInTheDocument();
    expect(screen.getByText("דיבור")).toBeInTheDocument();
  });
});
