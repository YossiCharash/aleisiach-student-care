import type {
  DetailOptionField,
  LegalStatus,
  MeetingRating,
  InvitableRole,
  UserRole,
  UserStatus,
} from "@/lib/api/types";

export const roleLabels: Record<UserRole, string> = {
  super_admin: "מנהל/ת מערכת",
  manager: "מנהל/ת",
  instructor: "מדריך/ה",
  professional_teacher: "מורה מקצועי/ת",
};

export const invitableRoleLabels: Record<InvitableRole, string> = {
  manager: roleLabels.manager,
  instructor: roleLabels.instructor,
  professional_teacher: roleLabels.professional_teacher,
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

export const detailOptionFieldLabels: Record<DetailOptionField, string> = {
  idd_severity: "דרגת מגבלה שכלית התפתחותית",
  medication_independence: "מידת עצמאות בלקיחת תרופות",
  expression_mode: "אופן הבעה עיקרי",
  language_comprehension: "מידת הבנת השפה",
  assistive_device: "אביזרי עזר פיזיים",
};

export const IDD_DIAGNOSIS_NAME = "מגבלה שכלית התפתחותית";

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

export function studentCountLabel(count: number): string {
  if (count === 1) {
    return "תלמיד אחד";
  }
  return `${count} תלמידים`;
}
