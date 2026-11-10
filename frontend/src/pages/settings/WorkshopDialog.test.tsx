import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UserResponse, WorkshopResponse } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { WorkshopDialog } from "@/pages/settings/WorkshopDialog";
import { usersApi, workshopsApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  workshopsApi: { create: vi.fn(), update: vi.fn() },
  usersApi: { list: vi.fn() },
}));

const createMock = vi.mocked(workshopsApi.create);
const updateMock = vi.mocked(workshopsApi.update);
const usersListMock = vi.mocked(usersApi.list);

function instructor(id: string, fullName: string): UserResponse {
  return {
    id,
    full_name: fullName,
    email: `${id}@example.com`,
    username: null,
    role: "instructor",
    workshop_id: null,
    status: "active",
    institution_id: "inst-1",
  };
}

const existing: WorkshopResponse = {
  id: "w1",
  name: "סדנה א׳",
  color: "#3F8420",
  instructors: [{ id: "u1", full_name: "דנה" }],
};

describe("WorkshopDialog", () => {
  beforeEach(() => {
    createMock.mockReset();
    updateMock.mockReset();
    usersListMock.mockReset();
    usersListMock.mockResolvedValue([instructor("u1", "דנה"), instructor("u2", "יעל")]);
  });

  it("creates a workshop with several instructors", async () => {
    createMock.mockResolvedValue(existing);

    renderWithClient(<WorkshopDialog open onOpenChange={() => undefined} />);
    await userEvent.type(screen.getByLabelText("שם הסדנה"), "סדנה ב׳");
    await userEvent.click(await screen.findByRole("checkbox", { name: "דנה" }));
    await userEvent.click(screen.getByRole("checkbox", { name: "יעל" }));
    await userEvent.click(screen.getByRole("button", { name: "שמירה" }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith({
        name: "סדנה ב׳",
        color: "#3F8420",
        instructor_ids: ["u1", "u2"],
      })
    );
  });

  it("pre-checks current instructors and lets one be removed", async () => {
    updateMock.mockResolvedValue(existing);

    renderWithClient(
      <WorkshopDialog open onOpenChange={() => undefined} workshop={existing} />
    );
    const dana = await screen.findByRole("checkbox", { name: "דנה" });
    expect(dana).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "יעל" })).not.toBeChecked();

    await userEvent.click(dana);
    await userEvent.click(screen.getByRole("button", { name: "שמירה" }));

    await waitFor(() =>
      expect(updateMock).toHaveBeenCalledWith("w1", {
        name: "סדנה א׳",
        color: "#3F8420",
        instructor_ids: [],
      })
    );
  });
});
