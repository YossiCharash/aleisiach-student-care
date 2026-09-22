import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { PreviousMeetingCard } from "@/pages/student/meetings/PreviousMeetingCard";
import type { MeetingResponse } from "@/lib/api/types";

function meeting(overrides: Partial<MeetingResponse> = {}): MeetingResponse {
  return {
    id: "m0",
    student_id: "s1",
    author_id: "u1",
    meeting_date: "2026-07-01",
    summary: "סיכום קודם",
    created_at: "2026-07-01T00:00:00Z",
    updated_at: "2026-07-01T00:00:00Z",
    strengths: [],
    areas_to_strengthen: [],
    plan_entries: [
      {
        skill_id: "sk2",
        skill_name_snapshot: "רחיצת ידיים",
        rating: "yellow",
        solutions: [{ solution_id: "so0", solution_text_snapshot: "תרגול יומי" }],
      },
    ],
    ...overrides,
  };
}

describe("PreviousMeetingCard", () => {
  it("shows the previous meeting summary and plan", () => {
    render(<PreviousMeetingCard meeting={meeting()} />);

    expect(screen.getByText(/^הישיבה הקודמת/)).toBeInTheDocument();
    expect(screen.getByText("סיכום קודם")).toBeInTheDocument();
    expect(screen.getByText("תרגול יומי")).toBeInTheDocument();
  });

  it("shows an empty-state when the previous meeting has a blank summary", () => {
    render(<PreviousMeetingCard meeting={meeting({ summary: "   " })} />);

    expect(screen.getByText("לא נכתב סיכום.")).toBeInTheDocument();
  });
});
