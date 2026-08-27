import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { RatingPill } from "@/components/RatingPill";

describe("RatingPill", () => {
  it("shows the Hebrew independence label for each rating", () => {
    render(<RatingPill rating="green" />);
    expect(screen.getByText("עצמאי")).toBeInTheDocument();
  });

  it("renders the supervised label for a yellow rating", () => {
    render(<RatingPill rating="yellow" />);
    expect(screen.getByText("בהשגחה")).toBeInTheDocument();
  });

  it("renders the dependent label for a red rating", () => {
    render(<RatingPill rating="red" />);
    expect(screen.getByText("בתלות")).toBeInTheDocument();
  });
});
