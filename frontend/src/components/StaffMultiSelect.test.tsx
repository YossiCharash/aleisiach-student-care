import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { StaffMultiSelect } from "@/components/StaffMultiSelect";
import { withAssigned } from "@/lib/utils/staff";

const MOR = { id: "u1", full_name: "מור" };
const DANA = { id: "u2", full_name: "דנה" };

describe("StaffMultiSelect", () => {
  it("shows the selected names on the trigger and a placeholder when empty", () => {
    const { rerender } = render(
      <StaffMultiSelect
        candidates={[MOR, DANA]}
        selected={["u1", "u2"]}
        onChange={vi.fn()}
      />
    );
    expect(screen.getByRole("button", { name: /מור, דנה/ })).toBeInTheDocument();

    rerender(
      <StaffMultiSelect candidates={[MOR, DANA]} selected={[]} onChange={vi.fn()} />
    );
    expect(screen.getByRole("button", { name: /בחירה/ })).toBeInTheDocument();
  });

  it("toggles a member from the dropdown and keeps the list open", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    render(
      <StaffMultiSelect candidates={[MOR, DANA]} selected={["u1"]} onChange={onChange} />
    );

    await user.click(screen.getByRole("button", { name: /מור/ }));
    expect(screen.getByRole("menuitemcheckbox", { name: "מור" })).toHaveAttribute(
      "aria-checked",
      "true"
    );
    await user.click(screen.getByRole("menuitemcheckbox", { name: "דנה" }));
    await user.click(screen.getByRole("menuitemcheckbox", { name: "מור" }));

    expect(onChange).toHaveBeenNthCalledWith(1, ["u1", "u2"]);
    expect(onChange).toHaveBeenNthCalledWith(2, []);
  });

  it("appends assigned members missing from the candidates once", () => {
    expect(withAssigned([MOR], [DANA, DANA, MOR])).toEqual([MOR, DANA]);
  });
});
