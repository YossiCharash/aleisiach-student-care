import { describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import type { StudentResponse } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { StudentActionsMenu } from "@/pages/student/StudentActionsMenu";

vi.mock("@/lib/api/endpoints", () => ({
  studentsApi: { update: vi.fn(), archive: vi.fn() },
  classesApi: { list: vi.fn().mockResolvedValue([]) },
}));

const student: StudentResponse = {
  id: "student-1",
  class_id: "class-1",
  full_name: "דנה",
  is_archived: false,
};

function renderMenu(): void {
  renderWithClient(
    <MemoryRouter>
      <StudentActionsMenu student={student} />
    </MemoryRouter>
  );
}

describe("StudentActionsMenu", () => {
  it("keeps both actions behind one trigger", async () => {
    renderMenu();

    expect(screen.queryByText("עריכת פרטים")).not.toBeInTheDocument();
    expect(screen.queryByText("העברה לארכיון")).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "פעולות נוספות" }));

    expect(await screen.findByText("עריכת פרטים")).toBeInTheDocument();
    expect(screen.getByText("העברה לארכיון")).toBeInTheDocument();
  });

  it("opens the edit dialog prefilled with the current name", async () => {
    renderMenu();

    await userEvent.click(screen.getByRole("button", { name: "פעולות נוספות" }));
    await userEvent.click(await screen.findByText("עריכת פרטים"));

    await waitFor(() => expect(screen.getByDisplayValue("דנה")).toBeInTheDocument());
  });

  it("asks for confirmation with a distinct label before archiving", async () => {
    renderMenu();

    await userEvent.click(screen.getByRole("button", { name: "פעולות נוספות" }));
    await userEvent.click(await screen.findByText("העברה לארכיון"));

    expect(
      await screen.findByRole("button", { name: "כן, להעביר לארכיון" })
    ).toBeInTheDocument();
  });
});
