import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CreateClassDialog } from "@/pages/classes/CreateClassDialog";
import { renderWithClient } from "@/test/renderWithClient";
import { classesApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  classesApi: { create: vi.fn() },
}));

const createMock = vi.mocked(classesApi.create);

describe("CreateClassDialog", () => {
  beforeEach(() => createMock.mockReset());

  it("creates a class and closes on success", async () => {
    createMock.mockResolvedValue({ id: "c9", name: "כיתה ג׳" });
    const onOpenChange = vi.fn();
    renderWithClient(<CreateClassDialog open onOpenChange={onOpenChange} />);

    await userEvent.type(screen.getByLabelText("שם הכיתה"), "כיתה ג׳");
    await userEvent.click(screen.getByRole("button", { name: "הוספה" }));

    expect(createMock).toHaveBeenCalledWith("כיתה ג׳");
    await waitFor(() => expect(onOpenChange).toHaveBeenCalledWith(false));
  });

  it("keeps the submit button disabled while the name is empty", () => {
    const onOpenChange = vi.fn();
    renderWithClient(<CreateClassDialog open onOpenChange={onOpenChange} />);

    expect(screen.getByRole("button", { name: "הוספה" })).toBeDisabled();
  });
});
