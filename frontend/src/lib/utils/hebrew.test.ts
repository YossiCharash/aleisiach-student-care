import { describe, expect, it } from "vitest";
import {
  formatDate,
  legalStatusLabels,
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

describe("date formatting", () => {
  it("renders a dash for a missing date", () => {
    expect(formatDate(null)).toBe("—");
  });

  it("formats an ISO date into a localized string", () => {
    expect(formatDate("2026-08-27")).toContain("2026");
  });
});
