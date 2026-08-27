import { describe, expect, it } from "vitest";
import { draftsToEntries, type EntryDraft } from "@/lib/meetings/buildEntries";

describe("draftsToEntries", () => {
  it("skips skills without a rating", () => {
    const drafts: Record<string, EntryDraft> = {
      "skill-1": { rating: null, solutionIds: [] },
      "skill-2": { rating: "green", solutionIds: [] },
    };
    const entries = draftsToEntries(drafts);
    expect(entries).toHaveLength(1);
    expect(entries[0].skill_id).toBe("skill-2");
  });

  it("drops solutions for a green rating", () => {
    const drafts: Record<string, EntryDraft> = {
      "skill-1": { rating: "green", solutionIds: ["sol-1", "sol-2"] },
    };
    expect(draftsToEntries(drafts)[0].solution_ids).toEqual([]);
  });

  it("keeps solutions for yellow and red ratings", () => {
    const drafts: Record<string, EntryDraft> = {
      "skill-yellow": { rating: "yellow", solutionIds: ["sol-1"] },
      "skill-red": { rating: "red", solutionIds: ["sol-2", "sol-3"] },
    };
    const byId = Object.fromEntries(
      draftsToEntries(drafts).map((entry) => [entry.skill_id, entry.solution_ids])
    );
    expect(byId["skill-yellow"]).toEqual(["sol-1"]);
    expect(byId["skill-red"]).toEqual(["sol-2", "sol-3"]);
  });

  it("returns an empty list when nothing is rated", () => {
    expect(draftsToEntries({})).toEqual([]);
  });
});
