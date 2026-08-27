import type { MeetingEntryRequest, MeetingRating } from "@/lib/api/types";

export interface EntryDraft {
  rating: MeetingRating | null;
  solutionIds: string[];
}

export function draftsToEntries(drafts: Record<string, EntryDraft>): MeetingEntryRequest[] {
  return Object.entries(drafts)
    .filter(([, draft]) => draft.rating !== null)
    .map(([skillId, draft]) => ({
      skill_id: skillId,
      rating: draft.rating as MeetingRating,
      solution_ids: draft.rating === "green" ? [] : draft.solutionIds,
    }));
}
