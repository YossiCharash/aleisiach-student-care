import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { renderWithClient } from "@/test/renderWithClient";
import { MeetingsOverviewPage } from "@/pages/MeetingsOverviewPage";
import { classesApi, meetingsApi, studentsApi } from "@/lib/api/endpoints";
import type {
  ClassResponse,
  MeetingOverviewItem,
  StudentResponse,
} from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  meetingsApi: { overview: vi.fn() },
  studentsApi: { list: vi.fn() },
  classesApi: { list: vi.fn() },
}));

const overviewMock = vi.mocked(meetingsApi.overview);
const listMock = vi.mocked(studentsApi.list);
const classesMock = vi.mocked(classesApi.list);

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
  { id: "s-maya", full_name: "מאיה ברק", class_id: "c2", is_archived: false },
];

const classes: ClassResponse[] = [
  { id: "c1", name: "כיתה א" },
  { id: "c2", name: "כיתה ב" },
];

describe("MeetingsOverviewPage", () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date(2026, 8, 15));
    overviewMock.mockResolvedValue(overview);
    listMock.mockResolvedValue(students);
    classesMock.mockResolvedValue(classes);
  });

  afterEach(() => vi.useRealTimers());

  function render(): void {
    renderWithClient(
      <MemoryRouter>
        <MeetingsOverviewPage />
      </MemoryRouter>
    );
  }

  it("lists only students without a meeting this month, grouped by class, linking to a new meeting", async () => {
    render();

    expect(await screen.findByText("כיתה א")).toBeInTheDocument();
    expect(screen.getByText("כיתה ב")).toBeInTheDocument();

    expect(screen.getByRole("link", { name: /איתי לוי/ })).toHaveAttribute(
      "href",
      "/students/s-itai?tab=meetings&new=1"
    );
    expect(screen.getByRole("link", { name: /מאיה ברק/ })).toHaveAttribute(
      "href",
      "/students/s-maya?tab=meetings&new=1"
    );

    expect(screen.queryByText("נועה כהן")).not.toBeInTheDocument();
  });

  it("shows an empty state when everyone already met this month", async () => {
    overviewMock.mockResolvedValue(
      students.map((student) => ({
        student_id: student.id,
        student_name: student.full_name,
        meeting_id: `m-${student.id}`,
        year: 2026,
        month: 9,
      }))
    );

    render();

    expect(
      await screen.findByText("כל התלמידים כבר נערכה להם ישיבה החודש.")
    ).toBeInTheDocument();
  });
});
