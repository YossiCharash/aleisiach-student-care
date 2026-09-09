import { describe, expect, it } from "vitest";
import { initials } from "@/lib/utils/initials";

describe("initials", () => {
  it("joins the first letter of the first two words", () => {
    expect(initials("אבי לוי")).toBe("א.ל");
  });

  it("uses the single letter of a one-word name", () => {
    expect(initials("אבי")).toBe("א");
  });

  it("ignores words beyond the second", () => {
    expect(initials("אבי בן לוי")).toBe("א.ב");
  });

  it("collapses extra whitespace", () => {
    expect(initials("  דנה   בר  ")).toBe("ד.ב");
  });

  it("returns an empty string for a blank name", () => {
    expect(initials("   ")).toBe("");
  });
});
