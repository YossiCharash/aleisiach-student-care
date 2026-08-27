import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PersonalSettingsPage } from "@/pages/PersonalSettingsPage";
import { renderWithClient } from "@/test/renderWithClient";
import { authApi } from "@/lib/api/endpoints";
import { ApiError } from "@/lib/api/client";
import type { UserResponse } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  authApi: { changePassword: vi.fn() },
}));

const user: UserResponse = {
  id: "u1",
  full_name: "מור",
  email: "mor@example.com",
  username: "mor",
  role: "manager",
  class_id: null,
  status: "active",
};

vi.mock("@/lib/auth/AuthContext", () => ({
  useAuth: () => ({ user }),
}));

const changePasswordMock = vi.mocked(authApi.changePassword);

async function fill(current: string, next: string, confirm: string): Promise<void> {
  await userEvent.type(screen.getByLabelText("סיסמה נוכחית"), current);
  await userEvent.type(screen.getByLabelText("סיסמה חדשה"), next);
  await userEvent.type(screen.getByLabelText("אימות סיסמה חדשה"), confirm);
  await userEvent.click(screen.getByRole("button", { name: "שינוי סיסמה" }));
}

describe("PersonalSettingsPage — change password", () => {
  beforeEach(() => {
    changePasswordMock.mockReset();
  });

  it("blocks submission when the confirmation does not match", async () => {
    renderWithClient(<PersonalSettingsPage />);
    await fill("old12345", "new12345", "different");

    expect(screen.getByText("הסיסמאות אינן תואמות.")).toBeInTheDocument();
    expect(changePasswordMock).not.toHaveBeenCalled();
  });

  it("blocks submission when the new password is too short", async () => {
    renderWithClient(<PersonalSettingsPage />);
    await fill("old12345", "short", "short");

    expect(screen.getByText(/לפחות 8 תווים/)).toBeInTheDocument();
    expect(changePasswordMock).not.toHaveBeenCalled();
  });

  it("submits the current and new password and confirms success", async () => {
    changePasswordMock.mockResolvedValue(undefined);
    renderWithClient(<PersonalSettingsPage />);
    await fill("old12345", "new12345", "new12345");

    expect(changePasswordMock).toHaveBeenCalledWith({
      current_password: "old12345",
      new_password: "new12345",
    });
    expect(await screen.findByText("הסיסמה שונתה בהצלחה.")).toBeInTheDocument();
  });

  it("surfaces the server message when the current password is wrong", async () => {
    changePasswordMock.mockRejectedValue(
      new ApiError(400, "invalid_current_password", "הסיסמה הנוכחית שגויה.")
    );
    renderWithClient(<PersonalSettingsPage />);
    await fill("wrongpass", "new12345", "new12345");

    expect(await screen.findByText("הסיסמה הנוכחית שגויה.")).toBeInTheDocument();
  });
});
