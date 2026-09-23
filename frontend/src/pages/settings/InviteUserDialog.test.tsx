import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { InviteUserDialog } from "@/pages/settings/InviteUserDialog";
import { authApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  authApi: {
    createInvitation: vi.fn(),
  },
}));

const createMock = vi.mocked(authApi.createInvitation);

async function fillFirstRow(): Promise<void> {
  await userEvent.type(screen.getByLabelText("שם מלא"), "מור");
  await userEvent.type(screen.getByLabelText("דוא״ל"), "mor@example.com");
}

describe("InviteUserDialog", () => {
  beforeEach(() => {
    createMock.mockReset();
    createMock.mockResolvedValue({} as never);
  });

  it("sends the invitation email by default", async () => {
    renderWithClient(<InviteUserDialog open onOpenChange={vi.fn()} />);
    await fillFirstRow();

    await userEvent.click(screen.getByRole("button", { name: "שליחת הזמנה" }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith(
        expect.objectContaining({ email: "mor@example.com", send_email: true })
      )
    );
  });

  it("confirms that the invitation email was sent", async () => {
    renderWithClient(<InviteUserDialog open onOpenChange={vi.fn()} />);
    await fillFirstRow();

    await userEvent.click(screen.getByRole("button", { name: "שליחת הזמנה" }));

    await waitFor(() =>
      expect(screen.getByText("ההזמנה נשלחה בהצלחה בדוא״ל.")).toBeInTheDocument()
    );
  });

  it("creates the user without an email when the toggle is cleared", async () => {
    renderWithClient(<InviteUserDialog open onOpenChange={vi.fn()} />);
    await fillFirstRow();

    await userEvent.click(screen.getByRole("checkbox"));
    await userEvent.click(screen.getByRole("button", { name: "הוספת משתמש" }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith(
        expect.objectContaining({ email: "mor@example.com", send_email: false })
      )
    );
  });
});
