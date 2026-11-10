import { describe, expect, it } from "vitest";
import { toggled } from "@/lib/utils/arrays";

describe("toggled", () => {
  it("appends the value when switched on", () => {
    expect(toggled(["a"], "b", true)).toEqual(["a", "b"]);
  });

  it("removes the value when switched off", () => {
    expect(toggled(["a", "b"], "a", false)).toEqual(["b"]);
  });
});
