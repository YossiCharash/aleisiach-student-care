import type { ReactNode } from "react";
import type { StudentDetailsResponse } from "@/lib/api/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

function filled(value: string | null | undefined): boolean {
  return typeof value === "string" && value.trim().length > 0;
}

export function TextBlock({
  label,
  value,
}: {
  label: string;
  value: string | null;
}): ReactNode {
  if (!filled(value)) {
    return null;
  }
  return (
    <div>
      <div className="mb-1 text-ink-muted">{label}</div>
      <div className="whitespace-pre-wrap font-medium text-ink">{value}</div>
    </div>
  );
}

export function CommunicationChannelCard({
  details,
}: {
  details: StudentDetailsResponse;
}): ReactNode {
  if (!filled(details.expression_mode) && !filled(details.language_comprehension)) {
    return null;
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>ערוץ תקשורת מועדף</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        {filled(details.expression_mode) && (
          <div>
            <span className="text-ink-muted">אופן הבעה עיקרי: </span>
            <span className="font-medium text-ink">{details.expression_mode}</span>
          </div>
        )}
        {filled(details.language_comprehension) && (
          <div>
            <span className="text-ink-muted">מידת הבנת השפה: </span>
            <span className="font-medium text-ink">{details.language_comprehension}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function EmotionalProfileCard({
  details,
}: {
  details: StudentDetailsResponse;
}): ReactNode {
  const hasContent = [
    details.interests_strengths,
    details.triggers,
    details.distress_early_signs,
    details.calming_methods,
  ].some(filled);
  if (!hasContent) {
    return null;
  }
  return (
    <Card>
      <CardHeader>
        <CardTitle>תעודת זהות רגשית</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 text-sm">
        <TextBlock label="תחומי עניין וחוזקות" value={details.interests_strengths} />
        <TextBlock label="גורמים מציפים / טריגרים" value={details.triggers} />
        <TextBlock label="סימנים מקדימים למצוקה" value={details.distress_early_signs} />
        <TextBlock label="דרכי הרגעה מומלצות" value={details.calming_methods} />
      </CardContent>
    </Card>
  );
}
