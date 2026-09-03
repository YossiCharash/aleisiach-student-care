import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { renderWithClient } from "@/test/renderWithClient";
import { MeetingsOverviewPage } from "@/pages/MeetingsOverviewPage";
import { meetingsApi, studentsApi } from "@/lib/api/endpoints";
import type { MeetingOverviewItem, StudentResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  meetingsApi: { overview: vi.fn() },
  studentsApi: { list: vi.fn() },
}));

const overviewMock = vi.mocked(meetingsApi.overview);
const listMock = vi.mocked(studentsApi.list);

const overview: MeetingOverviewItem[] = [
  {
    student_id: "s-noa",
    student_name: "נועה כהן",
    meeting_id: "m1",
    year: 2026,
    month: 9,
  },
  {
    student_id: "s-itai",
    student_name: "איתי לוי",
    meeting_id: "m2",
    year: 2026,
    month: 8,
  },
];

const students: StudentResponse[] = [
  { id: "s-noa", full_name: "נועה כהן", class_id: "c1", is_archived: false },
  { id: "s-itai", full_name: "איתי לוי", class_id: "c1", is_archived: false },
  { id: "s-maya", full_name: "מאיה ברק", class_id: "c1", is_archived: false },
];

describe("MeetingsOverviewPage", () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date(2026, 8, 15));
    overviewMock.mockResolvedValue(overview);
    listMock.mockResolvedValue(students);
  });

  afterEach(() => vi.useRealTimers());

  function render(): void {
    renderWithClient(
      <MemoryRouter>
        <MeetingsOverviewPage />
      </MemoryRouter>
    );
  }

  it("groups meetings by month and lists who has not met this month", async () => {
    render();

    expect(await screen.findByText("ספטמבר 2026")).toBeInTheDocument();
    expect(screen.getByText("אוגוסט 2026")).toBeInTheDocument();

    expect(screen.getByRole("link", { name: /נועה כהן/ })).toHaveAttribute(
      "href",
      "/students/s-noa"
    );
    expect(screen.getByRole("link", { name: /מאיה ברק/ })).toHaveAttribute(
      "href",
      "/students/s-maya"
    );
    expect(screen.getAllByRole("link", { name: /איתי לוי/ })).toHaveLength(2);
    expect(screen.getByText("טרם נערכה ישיבה")).toBeInTheDocument();
  });
});
