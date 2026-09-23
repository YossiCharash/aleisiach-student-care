import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConfirmWithPasswordDialog } from "@/components/ui/ConfirmWithPasswordDialog";

function renderDialog(overrides: Partial<Parameters<typeof ConfirmWithPasswordDialog>[0]> = {}) {
  const onConfirm = vi.fn();
  render(
    <ConfirmWithPasswordDialog
      open
      onOpenChange={vi.fn()}
      title="מחיקה לצמיתות"
      description="לא ניתן לשחזר."
      confirmLabel="מחיקה לצמיתות"
      pendingLabel="מוחק…"
      isPending={false}
      error={null}
      onConfirm={onConfirm}
      {...overrides}
    />
  );
  return { onConfirm };
}

describe("ConfirmWithPasswordDialog", () => {
  it("keeps the confirm button disabled until a password is typed", async () => {
    const user = userEvent.setup();
    renderDialog();

    const confirm = screen.getByRole("button", { name: "מחיקה לצמיתות" });
    expect(confirm).toBeDisabled();

    await user.type(screen.getByLabelText("אישור באמצעות הסיסמה שלך"), "secret123");
    expect(confirm).toBeEnabled();
  });

  it("submits the typed password", async () => {
    const user = userEvent.setup();
    const { onConfirm } = renderDialog();

    await user.type(screen.getByLabelText("אישור באמצעות הסיסמה שלך"), "secret123");
    await user.click(screen.getByRole("button", { name: "מחיקה לצמיתות" }));

    expect(onConfirm).toHaveBeenCalledWith("secret123");
  });

  it("shows the error message", () => {
    renderDialog({ error: "הסיסמה הנוכחית שגויה." });
    expect(screen.getByText("הסיסמה הנוכחית שגויה.")).toBeInTheDocument();
  });
});
