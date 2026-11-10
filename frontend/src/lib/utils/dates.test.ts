import { describe, expect, it } from "vitest";
import { todayIso } from "@/lib/utils/dates";

describe("todayIso", () => {
  it("formats the local calendar date as YYYY-MM-DD", () => {
    expect(todayIso(new Date(2026, 10, 10, 23, 30))).toBe("2026-11-10");
  });

  it("uses the local date just after midnight", () => {
    expect(todayIso(new Date(2026, 0, 1, 0, 15))).toBe("2026-01-01");
  });
});
