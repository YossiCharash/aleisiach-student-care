import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { EditClassDialog } from "@/pages/classes/EditClassDialog";
import { renderWithClient } from "@/test/renderWithClient";
import { classesApi, studentsApi } from "@/lib/api/endpoints";
import type { ClassResponse, StudentResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  classesApi: { list: vi.fn(), rename: vi.fn(), archive: vi.fn() },
  studentsApi: { list: vi.fn(), update: vi.fn() },
}));

const classes: ClassResponse[] = [
  { id: "c1", name: "כיתה א׳" },
  { id: "c2", name: "כיתה ב׳" },
];
const students: StudentResponse[] = [
  { id: "s1", full_name: "נועה", class_id: "c1", is_archived: false },
  { id: "s2", full_name: "איתי", class_id: "c2", is_archived: false },
];
const classItem: ClassResponse = { id: "c1", name: "כיתה א׳" };

const renameMock = vi.mocked(classesApi.rename);
const archiveMock = vi.mocked(classesApi.archive);
const updateMock = vi.mocked(studentsApi.update);

function renderDialog(onOpenChange = vi.fn()): {
  onOpenChange: ReturnType<typeof vi.fn>;
} {
  renderWithClient(
    <EditClassDialog classItem={classItem} open onOpenChange={onOpenChange} />
  );
  return { onOpenChange };
}

describe("EditClassDialog", () => {
  beforeEach(() => {
    vi.mocked(classesApi.list).mockResolvedValue(classes);
    vi.mocked(studentsApi.list).mockResolvedValue(students);
    renameMock.mockReset().mockResolvedValue({ id: "c1", name: "כיתה א׳ חדשה" });
    archiveMock.mockReset().mockResolvedValue({ id: "c1", name: "כיתה א׳" });
    updateMock.mockReset();
  });

  it("renames the class", async () => {
    renderDialog();
    const input = await screen.findByLabelText("שם הכיתה");
    await userEvent.clear(input);
    await userEvent.type(input, "כיתה א׳ חדשה");
    await userEvent.click(screen.getByRole("button", { name: "שמירת שם" }));

    expect(renameMock).toHaveBeenCalledWith("c1", "כיתה א׳ חדשה");
  });

  it("adds an outside student to the class", async () => {
    renderDialog();
    await screen.findByRole("option", { name: "איתי" });
    await userEvent.selectOptions(screen.getByLabelText("הוספת תלמיד לכיתה"), "s2");

    expect(updateMock).toHaveBeenCalledWith("s2", {
      full_name: "איתי",
      class_id: "c1",
    });
  });

  it("archives the class and closes", async () => {
    const { onOpenChange } = renderDialog();
    await userEvent.click(screen.getByRole("button", { name: "העברה לארכיון" }));

    expect(archiveMock).toHaveBeenCalledWith("c1");
    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
  });

  it("does not offer instructor editing", async () => {
    renderDialog();
    await screen.findByLabelText("שם הכיתה");
    expect(screen.queryByLabelText("מדריך הכיתה")).not.toBeInTheDocument();
  });
});
