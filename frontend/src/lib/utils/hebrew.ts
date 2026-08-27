import type { LegalStatus, MeetingRating, UserRole, UserStatus } from "@/lib/api/types";

export const roleLabels: Record<UserRole, string> = {
  manager: "מנהל/ת",
  instructor: "מדריך/ה",
  professional_teacher: "מורה מקצועי/ת",
};

export const userStatusLabels: Record<UserStatus, string> = {
  invited: "הוזמן",
  active: "פעיל",
  disabled: "מושבת",
};

export const ratingLabels: Record<MeetingRating, string> = {
  green: "עצמאי",
  yellow: "בהשגחה",
  red: "בתלות",
};

export const legalStatusLabels: Record<LegalStatus, string> = {
  guardian_appointed: "מונה אפוטרופוס",
  parents_are_guardians: "ההורים הם האפוטרופוסים",
};

const monthNames = [
  "ינואר",
  "פברואר",
  "מרץ",
  "אפריל",
  "מאי",
  "יוני",
  "יולי",
  "אוגוסט",
  "ספטמבר",
  "אוקטובר",
  "נובמבר",
  "דצמבר",
];

export function monthName(month: number): string {
  return monthNames[month - 1] ?? String(month);
}

export function formatMonthYear(year: number, month: number): string {
  return `${monthName(month)} ${year}`;
}

export function formatDate(iso: string | null): string {
  if (!iso) {
    return "—";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return new Intl.DateTimeFormat("he-IL", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}
