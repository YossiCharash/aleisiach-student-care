import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PasswordInput } from "@/components/ui/PasswordInput";

describe("PasswordInput", () => {
  it("hides the password by default", () => {
    render(<PasswordInput aria-label="סיסמה" />);
    expect(screen.getByLabelText("סיסמה")).toHaveAttribute("type", "password");
    expect(screen.getByRole("button", { name: "הצגת הסיסמה" })).toBeInTheDocument();
  });

  it("reveals the password when the toggle is clicked", async () => {
    const user = userEvent.setup();
    render(<PasswordInput aria-label="סיסמה" />);

    await user.click(screen.getByRole("button", { name: "הצגת הסיסמה" }));

    expect(screen.getByLabelText("סיסמה")).toHaveAttribute("type", "text");
    expect(screen.getByRole("button", { name: "הסתרת הסיסמה" })).toBeInTheDocument();
  });

  it("hides the password again when toggled back", async () => {
    const user = userEvent.setup();
    render(<PasswordInput aria-label="סיסמה" />);
    const toggle = () => screen.getByRole("button");

    await user.click(toggle());
    await user.click(toggle());

    expect(screen.getByLabelText("סיסמה")).toHaveAttribute("type", "password");
  });
});
