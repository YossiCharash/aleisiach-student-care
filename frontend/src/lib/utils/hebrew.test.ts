import { describe, expect, it } from "vitest";
import {
  formatDate,
  formatMonthYear,
  legalStatusLabels,
  monthName,
  ratingLabels,
  roleLabels,
  userStatusLabels,
} from "@/lib/utils/hebrew";

describe("hebrew labels", () => {
  it("maps every role to a Hebrew label", () => {
    expect(roleLabels.manager).toBe("מנהל/ת");
    expect(roleLabels.instructor).toBe("מדריך/ה");
    expect(roleLabels.professional_teacher).toBe("מורה מקצועי/ת");
  });

  it("maps ratings to Hebrew independence levels", () => {
    expect(ratingLabels.green).toBe("עצמאי");
    expect(ratingLabels.yellow).toBe("בהשגחה");
    expect(ratingLabels.red).toBe("בתלות");
  });

  it("maps statuses and legal statuses", () => {
    expect(userStatusLabels.invited).toBe("הוזמן");
    expect(legalStatusLabels.parents_are_guardians).toBe("ההורים הם האפוטרופוסים");
  });
});

describe("date and month formatting", () => {
  it("returns the Hebrew month name", () => {
    expect(monthName(1)).toBe("ינואר");
    expect(monthName(12)).toBe("דצמבר");
  });

  it("falls back to the number for an out-of-range month", () => {
    expect(monthName(13)).toBe("13");
  });

  it("combines month and year", () => {
    expect(formatMonthYear(2026, 3)).toBe("מרץ 2026");
  });

  it("renders a dash for a missing date", () => {
    expect(formatDate(null)).toBe("—");
  });

  it("formats an ISO date into a localized string", () => {
    expect(formatDate("2026-08-27")).toContain("2026");
  });
});
