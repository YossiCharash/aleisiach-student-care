import type {
  IncidentNature,
  IncidentReferral,
  IncidentReportFields,
  IncidentReportType,
} from "@/lib/api/types";

export const REPORT_TYPES: { value: IncidentReportType; label: string }[] = [
  { value: "internal", label: "אירוע חריג – דיווח פנימי" },
  { value: "external", label: "אירוע חריג – דיווח חיצוני" },
];

export const NATURES: { value: IncidentNature; label: string }[] = [
  { value: "accident_injury_death", label: "תאונה / פגיעה פיזית / פטירה" },
  { value: "violence", label: "אלימות" },
  { value: "property_damage", label: "פגיעה ברכוש" },
  { value: "prohibited_substances", label: "שימוש בחומרים אסורים" },
  { value: "other", label: "אחר" },
];

export const REFERRALS: { value: IncidentReferral; label: string }[] = [
  { value: "internal_event", label: "אירוע פנימי" },
  { value: "guardian", label: "אפוטרופוס / תומך החלטה" },
  { value: "welfare_social_worker", label: "עו״ס הרווחה" },
  { value: "statutory_social_worker", label: "עו״ס על פי חוק" },
  { value: "police", label: "משטרה" },
  { value: "framework_supervisor", label: "מפקח על המסגרת" },
  { value: "other", label: "אחר" },
];

type TextKey = {
  [K in keyof IncidentReportFields]: IncidentReportFields[K] extends string ? K : never;
}[keyof IncidentReportFields];

export const EVENT_SECTIONS: { key: TextKey; title: string }[] = [
  { key: "description", title: "תיאור האירוע" },
  { key: "staff_present", title: "אנשי צוות שנכחו באירוע" },
  {
    key: "affected_service_recipients",
    title: "מקבלי שירות שהיו נוכחים באירוע והושפעו מכך ובאיזה אופן?",
  },
  { key: "warning_signs", title: "האם היו סימנים מקדימים לאירוע?" },
  {
    key: "actions_taken",
    title: "סיכום הפעולות שבוצעו ע״י המדווח ואנשי הצוות האחרים",
  },
];

export const LESSON_SECTIONS: { key: TextKey; title: string }[] = [
  { key: "incident_causes", title: "הסיבות לאירוע" },
  { key: "was_preventable", title: "האם היה ניתן למנוע את האירוע" },
  { key: "lessons_learned", title: "לקחים שהופקו מהאירוע" },
  {
    key: "corrective_action_plan",
    title: "הכנת תכנית לפעולה מתקנת ליישום הלקחים",
  },
];

export const ATTACHMENT_NOTE = "יש לצרף לטופס דו״ח מרפאה / משטרה / אחר (אם הייתה פנייה)";

export function emptyIncidentFields(
  eventDate: string,
  fillerName: string
): IncidentReportFields {
  return {
    event_date: eventDate,
    event_time: null,
    location: "",
    reporter_name_role: "",
    report_type: null,
    natures: [],
    nature_other: "",
    description: "",
    staff_present: "",
    affected_service_recipients: "",
    warning_signs: "",
    actions_taken: "",
    referrals: [],
    referral_other: "",
    decision_reasons: "",
    manager_updated_date: null,
    manager_updated_time: null,
    incident_causes: "",
    was_preventable: "",
    lessons_learned: "",
    corrective_action_plan: "",
    filler_name: fillerName,
    filler_role: "",
  };
}

export function shortTime(value: string | null): string {
  return value ? value.slice(0, 5) : "";
}
