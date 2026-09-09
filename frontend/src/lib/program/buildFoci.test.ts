import { describe, expect, it } from "vitest";
import { focusDraftsToEntries } from "@/lib/program/buildFoci";

describe("focusDraftsToEntries", () => {
  it("maps each draft to a skill_id + rating entry", () => {
    const entries = focusDraftsToEntries({ sk1: "green", sk2: "red" });

    expect(entries).toEqual([
      { skill_id: "sk1", rating: "green" },
      { skill_id: "sk2", rating: "red" },
    ]);
  });

  it("returns an empty list when there are no drafts", () => {
    expect(focusDraftsToEntries({})).toEqual([]);
  });
});
