import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FocusRatingRow } from "@/pages/student/program/FocusRatingRow";
import type { SkillTreeNode } from "@/lib/api/types";

const skill: SkillTreeNode = { id: "sk1", name: "רחיצת ידיים", solutions: [] };

describe("FocusRatingRow", () => {
  it("selects the clicked rating", async () => {
    const onChange = vi.fn();
    render(<FocusRatingRow skill={skill} rating={null} onChange={onChange} />);

    await userEvent.click(screen.getByRole("radio", { name: "עצמאי" }));

    expect(onChange).toHaveBeenCalledWith("green");
  });

  it("toggles the active rating off when clicked again", async () => {
    const onChange = vi.fn();
    render(<FocusRatingRow skill={skill} rating="yellow" onChange={onChange} />);

    await userEvent.click(screen.getByRole("radio", { name: "בהשגחה" }));

    expect(onChange).toHaveBeenCalledWith(null);
  });

  it("marks only the active rating as checked", () => {
    render(<FocusRatingRow skill={skill} rating="red" onChange={vi.fn()} />);

    expect(screen.getByRole("radio", { name: "בתלות" })).toHaveAttribute(
      "aria-checked",
      "true"
    );
    expect(screen.getByRole("radio", { name: "עצמאי" })).toHaveAttribute(
      "aria-checked",
      "false"
    );
  });
});
