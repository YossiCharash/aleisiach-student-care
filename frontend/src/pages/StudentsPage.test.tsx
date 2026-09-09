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
];

function render(): void {
  renderWithClient(
    <MemoryRouter>
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
});
