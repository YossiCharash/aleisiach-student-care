import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FocusRatingRow } from "@/pages/student/program/FocusRatingRow";
import type { SkillTreeNode } from "@/lib/api/types";

const skill: SkillTreeNode = {
  id: "sk1",
  name: "רחיצת ידיים",
  green_text: "עצמאי מלא",
  yellow_text: "זקוק לעידוד",
  red_text: "תלוי לחלוטין",
  solutions: [],
};

describe("FocusRatingRow", () => {
  it("shows the per-skill rating descriptions", () => {
    render(<FocusRatingRow skill={skill} rating={null} onChange={vi.fn()} />);

    expect(screen.getByRole("radio", { name: "עצמאי מלא" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "זקוק לעידוד" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "תלוי לחלוטין" })).toBeInTheDocument();
  });

  it("selects the clicked rating", async () => {
    const onChange = vi.fn();
    render(<FocusRatingRow skill={skill} rating={null} onChange={onChange} />);

    await userEvent.click(screen.getByRole("radio", { name: "עצמאי מלא" }));

    expect(onChange).toHaveBeenCalledWith("green");
  });

  it("toggles the active rating off when clicked again", async () => {
    const onChange = vi.fn();
    render(<FocusRatingRow skill={skill} rating="yellow" onChange={onChange} />);

    await userEvent.click(screen.getByRole("radio", { name: "זקוק לעידוד" }));

    expect(onChange).toHaveBeenCalledWith(null);
  });

  it("never falls back to the fixed clinical words when a description is empty", () => {
    const blank: SkillTreeNode = {
      id: "sk2",
      name: "ללא תיאור",
      green_text: "",
      yellow_text: "",
      red_text: "",
      solutions: [],
    };
    render(<FocusRatingRow skill={blank} rating={null} onChange={vi.fn()} />);

    expect(screen.queryByText("עצמאי")).not.toBeInTheDocument();
    expect(screen.queryByText("בהשגחה")).not.toBeInTheDocument();
    expect(screen.queryByText("בתלות")).not.toBeInTheDocument();
    expect(screen.getAllByText("—")).toHaveLength(3);
  });

  it("marks only the active rating as checked", () => {
    render(<FocusRatingRow skill={skill} rating="red" onChange={vi.fn()} />);

    expect(screen.getByRole("radio", { name: "תלוי לחלוטין" })).toHaveAttribute(
      "aria-checked",
      "true"
    );
    expect(screen.getByRole("radio", { name: "עצמאי מלא" })).toHaveAttribute(
      "aria-checked",
      "false"
    );
  });
});
