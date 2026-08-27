import type { ReactNode } from "react";
import type { MeetingRating } from "@/lib/api/types";
import { ratingLabels } from "@/lib/utils/hebrew";
import { cn } from "@/lib/utils/cn";

const toneClass: Record<MeetingRating, string> = {
  green: "bg-accent-50 text-accent-700 ring-accent-200",
  yellow: "bg-amber-50 text-amber-700 ring-amber-200",
  red: "bg-red-50 text-red-700 ring-red-200",
};

const dotClass: Record<MeetingRating, string> = {
  green: "bg-rating-green",
  yellow: "bg-rating-yellow",
  red: "bg-rating-red",
};

export function RatingPill({ rating }: { rating: MeetingRating }): ReactNode {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        toneClass[rating]
      )}
    >
      <span className={cn("h-2 w-2 rounded-full", dotClass[rating])} aria-hidden />
      {ratingLabels[rating]}
    </span>
  );
}
