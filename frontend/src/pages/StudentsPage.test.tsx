import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import type { WorkshopResponse, StudentResponse } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { StudentsPage } from "@/pages/StudentsPage";
import { UNKNOWN_WORKSHOP_LABEL } from "@/lib/students/groupByWorkshop";

const listStudents = vi.hoisted(() => vi.fn());
const listClasses = vi.hoisted(() => vi.fn());

vi.mock("@/lib/api/endpoints", () => ({
  studentsApi: { list: listStudents },
  workshopsApi: { list: listClasses },
}));
vi.mock("@/lib/auth/AuthContext", () => ({
  useAuth: () => ({ user: { id: "u1", full_name: "מור", role: "manager" } }),
}));
vi.mock("@/pages/students/CreateStudentDialog", () => ({
  CreateStudentDialog: () => null,
}));

const students: StudentResponse[] = [
  { id: "s1", workshop_id: "c1", full_name: "איתי", is_archived: false },
];
const classes: WorkshopResponse[] = [
  {
    id: "c1",
    name: "סדנה א׳",
    color: "#3F8420",
    instructor_id: null,
    instructor_name: null,
  },
  {
    id: "c2",
    name: "סדנה ב׳",
    color: "#E6B800",
    instructor_id: null,
    instructor_name: null,
  },
];

const studentsInBothWorkshops: StudentResponse[] = [
  { id: "s1", workshop_id: "c1", full_name: "איתי", is_archived: false },
  { id: "s2", workshop_id: "c2", full_name: "נועה", is_archived: false },
];

function render(path = "/students"): void {
  renderWithClient(
    <MemoryRouter initialEntries={[path]}>
      <StudentsPage />
    </MemoryRouter>
  );
}

describe("StudentsPage", () => {
  beforeEach(() => {
    listStudents.mockReset();
    listClasses.mockReset();
  });

  it("waits for the class names before grouping", async () => {
    listStudents.mockResolvedValue(students);
    let releaseClasses: (value: WorkshopResponse[]) => void = () => {};
    listClasses.mockReturnValue(
      new Promise<WorkshopResponse[]>((resolve) => {
        releaseClasses = resolve;
      })
    );

    render();

    await waitFor(() => expect(listStudents).toHaveBeenCalled());
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50));
    });

    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.queryByText("איתי")).not.toBeInTheDocument();
    expect(screen.queryByText(UNKNOWN_WORKSHOP_LABEL)).not.toBeInTheDocument();

    releaseClasses(classes);

    expect(await screen.findByText("איתי")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /סדנה א׳/ })).toBeInTheDocument();
    expect(screen.queryByText(UNKNOWN_WORKSHOP_LABEL)).not.toBeInTheDocument();
  });

  it("surfaces an error when the class list fails instead of mislabelling students", async () => {
    listStudents.mockResolvedValue(students);
    listClasses.mockRejectedValue(new Error("נפילת רשת"));

    render();

    expect(await screen.findByText(/נפילת רשת/)).toBeInTheDocument();
    expect(screen.queryByText(UNKNOWN_WORKSHOP_LABEL)).not.toBeInTheDocument();
  });
  it("offers a chip for every workshop plus an all-workshops chip", async () => {
    listStudents.mockResolvedValue(studentsInBothWorkshops);
    listClasses.mockResolvedValue(classes);

    render();

    expect(await screen.findByRole("link", { name: "כל הסדנאות" })).toHaveAttribute(
      "aria-current",
      "page"
    );
    expect(screen.getByRole("link", { name: "סדנה א׳" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "סדנה ב׳" })).toBeInTheDocument();
  });

  it("marks the filtered workshop as current and lists only its students", async () => {
    listStudents.mockResolvedValue(studentsInBothWorkshops);
    listClasses.mockResolvedValue(classes);

    render("/students?workshop=c1");

    expect(await screen.findByRole("link", { name: "סדנה א׳" })).toHaveAttribute(
      "aria-current",
      "page"
    );
    expect(screen.getByRole("link", { name: "כל הסדנאות" })).not.toHaveAttribute(
      "aria-current"
    );
    expect(screen.getByText("איתי")).toBeInTheDocument();
    expect(screen.queryByText("נועה")).not.toBeInTheDocument();
  });

  it("clears the filter through the all-workshops chip", async () => {
    listStudents.mockResolvedValue(studentsInBothWorkshops);
    listClasses.mockResolvedValue(classes);

    render("/students?workshop=c1");

    expect(await screen.findByRole("link", { name: "כל הסדנאות" })).toHaveAttribute(
      "href",
      "/students"
    );
  });
});
