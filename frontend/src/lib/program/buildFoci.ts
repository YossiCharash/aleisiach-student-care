import type { FocusRatingRequest, MeetingRating } from "@/lib/api/types";

export type FocusDraft = Record<string, MeetingRating>;

export function focusDraftsToEntries(drafts: FocusDraft): FocusRatingRequest[] {
  return Object.entries(drafts).map(([skillId, rating]) => ({
    skill_id: skillId,
    rating,
  }));
}
