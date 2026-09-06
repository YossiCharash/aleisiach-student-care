import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { UserResponse } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { UsersArea } from "@/pages/settings/UsersArea";
import { usersApi } from "@/lib/api/endpoints";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  usersApi: {
    list: vi.fn(),
    resendInvitation: vi.fn(),
    disable: vi.fn(),
    enable: vi.fn(),
  },
}));

vi.mock("@/pages/settings/InviteUserDialog", () => ({
  InviteUserDialog: () => null,
}));
vi.mock("@/pages/settings/EditUserDialog", () => ({
  EditUserDialog: () => null,
}));

const listMock = vi.mocked(usersApi.list);
const resendMock = vi.mocked(usersApi.resendInvitation);

function user(overrides: Partial<UserResponse>): UserResponse {
  return {
    id: "u1",
    full_name: "מור",
    email: "mor@example.com",
    username: null,
    role: "instructor",
    class_id: null,
    status: "active",
    institution_id: "inst-1",
    ...overrides,
  };
}

describe("UsersArea", () => {
  beforeEach(() => {
    listMock.mockReset();
    resendMock.mockReset();
    useAuth.mockReturnValue({ user: user({ id: "boss", role: "manager" }) });
  });

  it("offers a resend-invitation button only for invited users", async () => {
    listMock.mockResolvedValue([
      user({ id: "a", full_name: "דנה", status: "active" }),
      user({ id: "b", full_name: "רון", status: "invited" }),
    ]);
    renderWithClient(<UsersArea />);

    const invitedRow = (await screen.findByText("רון")).closest("tr")!;
    const activeRow = screen.getByText("דנה").closest("tr")!;

    expect(
      within(invitedRow).getByRole("button", { name: "שליחת קישור התחברות" })
    ).toBeInTheDocument();
    expect(
      within(activeRow).queryByRole("button", { name: "שליחת קישור התחברות" })
    ).not.toBeInTheDocument();
  });

  it("sends a new login link and confirms on success", async () => {
    listMock.mockResolvedValue([user({ id: "b", full_name: "רון", status: "invited" })]);
    resendMock.mockResolvedValue(user({ id: "b", status: "invited" }));
    renderWithClient(<UsersArea />);

    await userEvent.click(
      await screen.findByRole("button", { name: "שליחת קישור התחברות" })
    );

    expect(resendMock).toHaveBeenCalledWith("b");
    await waitFor(() =>
      expect(screen.getByText("קישור התחברות חדש נשלח בדוא״ל.")).toBeInTheDocument()
    );
  });
});
