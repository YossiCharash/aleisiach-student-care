import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UserResponse, WorkshopResponse } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { WorkshopsArea } from "@/pages/settings/WorkshopsArea";
import { usersApi, workshopsApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  workshopsApi: {
    list: vi.fn(),
    listArchived: vi.fn(),
    archive: vi.fn(),
    restore: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  usersApi: { list: vi.fn() },
}));

const listMock = vi.mocked(workshopsApi.list);
const archiveMock = vi.mocked(workshopsApi.archive);
const usersListMock = vi.mocked(usersApi.list);

function workshop(overrides: Partial<WorkshopResponse>): WorkshopResponse {
  return {
    id: "w1",
    name: "סדנה א׳",
    color: "#3F8420",
    instructor_id: null,
    instructor_name: null,
    ...overrides,
  };
}

function instructor(): UserResponse {
  return {
    id: "u1",
    full_name: "דנה",
    email: "dana@example.com",
    username: null,
    role: "instructor",
    workshop_id: "w1",
    status: "active",
    institution_id: "inst-1",
  };
}

describe("WorkshopsArea", () => {
  beforeEach(() => {
    listMock.mockReset();
    archiveMock.mockReset();
    usersListMock.mockReset();
    usersListMock.mockResolvedValue([instructor()]);
  });

  it("lists workshops with their instructor name", async () => {
    listMock.mockResolvedValue([
      workshop({ instructor_id: "u1", instructor_name: "דנה" }),
    ]);

    renderWithClient(<WorkshopsArea />);

    expect(await screen.findByText("סדנה א׳")).toBeInTheDocument();
    expect(screen.getByText("דנה")).toBeInTheDocument();
  });

  it("shows a placeholder when a workshop has no instructor", async () => {
    listMock.mockResolvedValue([workshop({})]);

    renderWithClient(<WorkshopsArea />);

    expect(await screen.findByText("ללא מדריך")).toBeInTheDocument();
  });

  it("opens the create dialog from the new-workshop button", async () => {
    listMock.mockResolvedValue([]);

    renderWithClient(<WorkshopsArea />);
    await screen.findByText("אין סדנאות עדיין.");

    await userEvent.click(screen.getByRole("button", { name: "סדנה חדשה" }));

    expect(await screen.findByLabelText("שם הסדנה")).toBeInTheDocument();
    expect(screen.getByLabelText("צבע הסדנה")).toBeInTheDocument();
  });

  it("archives a workshop", async () => {
    listMock.mockResolvedValue([workshop({})]);
    archiveMock.mockResolvedValue(workshop({}));

    renderWithClient(<WorkshopsArea />);
    await screen.findByText("סדנה א׳");

    await userEvent.click(screen.getByRole("button", { name: "העברה לארכיון" }));

    await waitFor(() => expect(archiveMock).toHaveBeenCalledWith("w1"));
  });
});
