import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { ClassesPage } from "@/pages/ClassesPage";
import { renderWithClient } from "@/test/renderWithClient";
import { classesApi, studentsApi, usersApi } from "@/lib/api/endpoints";
import type { ClassResponse, StudentResponse, UserResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  classesApi: { list: vi.fn(), listArchived: vi.fn(), rename: vi.fn(), archive: vi.fn() },
  studentsApi: { list: vi.fn(), update: vi.fn() },
  usersApi: { list: vi.fn() },
}));

const classes: ClassResponse[] = [{ id: "c1", name: "כיתה א׳" }];
const students: StudentResponse[] = [
  { id: "s1", full_name: "נועה", class_id: "c1", is_archived: false },
];
const users: UserResponse[] = [
  {
    id: "u1",
    full_name: "דנה",
    email: "dana@example.com",
    username: "dana",
    role: "instructor",
    class_id: "c1",
    status: "active",
    institution_id: "i1",
  },
];

describe("ClassesPage", () => {
  beforeEach(() => {
    vi.mocked(classesApi.list).mockResolvedValue(classes);
    vi.mocked(classesApi.listArchived).mockResolvedValue([]);
    vi.mocked(studentsApi.list).mockResolvedValue(students);
    vi.mocked(usersApi.list).mockResolvedValue(users);
  });

  function render(): void {
    renderWithClient(
      <MemoryRouter>
        <ClassesPage />
      </MemoryRouter>
    );
  }

  it("shows each class with its instructor and student count", async () => {
    render();

    expect(await screen.findByText("כיתה א׳")).toBeInTheDocument();
    expect(screen.getByText("מדריך: דנה")).toBeInTheDocument();
    expect(screen.getByText("תלמיד אחד")).toBeInTheDocument();
  });

  it("opens the editor from the class gear", async () => {
    render();
    await screen.findByText("כיתה א׳");

    await userEvent.click(screen.getByRole("button", { name: "עריכת כיתה" }));

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "עריכת כיתה" })).toBeInTheDocument()
    );
  });
});
