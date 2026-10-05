import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BrandLogo } from "./BrandLogo";

describe("BrandLogo", () => {
  it("renders the brand logo image", () => {
    render(<BrandLogo />);
    const image = screen.getByRole("img", { name: "עלי שיח" });
    expect(image).toHaveAttribute("src", "/logo.png");
  });

  it("is animated by default and can be disabled", () => {
    const { rerender, container } = render(<BrandLogo />);
    expect(container.querySelector(".brand-logo")).toHaveClass("is-animated");

    rerender(<BrandLogo animated={false} />);
    expect(container.querySelector(".brand-logo")).not.toHaveClass("is-animated");
  });
});
