import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StaffChipPicker } from "@/components/StaffChipPicker";
import { withAssigned } from "@/lib/utils/staff";

const MOR = { id: "u1", full_name: "מור" };
const DANA = { id: "u2", full_name: "דנה" };

describe("StaffChipPicker", () => {
  it("toggles a member in and out of the selection", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <StaffChipPicker candidates={[MOR, DANA]} selected={["u1"]} onChange={onChange} />
    );

    expect(screen.getByRole("button", { name: "מור" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
    await user.click(screen.getByRole("button", { name: "דנה" }));
    await user.click(screen.getByRole("button", { name: "מור" }));

    expect(onChange).toHaveBeenNthCalledWith(1, ["u1", "u2"]);
    expect(onChange).toHaveBeenNthCalledWith(2, []);
  });

  it("appends assigned members missing from the candidates once", () => {
    expect(withAssigned([MOR], [DANA, DANA, MOR])).toEqual([MOR, DANA]);
  });
});
