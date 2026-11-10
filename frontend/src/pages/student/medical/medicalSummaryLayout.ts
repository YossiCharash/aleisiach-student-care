import type { MedicalSummaryFields, MedicalSummaryResponse } from "@/lib/api/types";

type KeysOf<T> = {
  [K in keyof MedicalSummaryFields]: MedicalSummaryFields[K] extends T ? K : never;
}[keyof MedicalSummaryFields];

export type TextKey = KeysOf<string>;
export type OptionKey = KeysOf<string[]>;
export type FlagKey = KeysOf<boolean | null>;

export interface Option {
  value: string;
  label: string;
}

export type LayoutItem =
  | { kind: "text"; key: TextKey; label: string; multiline?: boolean }
  | {
      kind: "options";
      key: OptionKey;
      label: string;
      other?: { key: TextKey; when: string };
    }
  | { kind: "flag"; key: FlagKey; label: string }
  | { kind: "date"; key: "epilepsy_last_seizure"; label: string };

export interface LayoutSection {
  title: string;
  items: LayoutItem[];
  note?: string;
}

export const OPTIONS: Record<OptionKey, Option[]> = {
  lives_with: [
    { value: "community_housing", label: "דיור בקהילה" },
    { value: "parents", label: "עם ההורים" },
    { value: "alone", label: "לבד" },
    { value: "partner", label: "עם בן/בת זוג" },
  ],
  dental_treatment: [
    { value: "unknown", label: "לא ידוע" },
    { value: "follow_up", label: "במעקב" },
    { value: "needs_rehabilitation", label: "זקוק לשיקום פה" },
  ],
  dentures: [
    { value: "fixed", label: "קבועות" },
    { value: "implants", label: "שתלים" },
    { value: "removable", label: "תותבת" },
  ],
  skin_integrity: [
    { value: "intact", label: "תקין" },
    { value: "not_intact", label: "לא תקין" },
  ],
  comprehension: [
    { value: "complex_instructions", label: "מבין הוראות מורכבות" },
    { value: "simple_instructions", label: "מבין הוראות פשוטות" },
    { value: "gestures", label: "מבין ג׳סטות והדגמות ללא מילים" },
    { value: "none", label: "אין הבנה מתאימה להוראות" },
  ],
  communication: [
    { value: "independent", label: "מתבטא באופן עצמאי וברור" },
    { value: "single_words", label: "מתבטא במילים בודדות" },
    { value: "alternative", label: "מתקשר בתקשורת חליפית (פלט / לוח / אחר)" },
  ],
  speech: [
    { value: "clear", label: "דיבורו ברור" },
    { value: "articulation", label: "יש הפרעות היגוי עקביות" },
    { value: "unclear", label: "דיבורו מסורבל וקשה להבינו" },
    { value: "nonverbal", label: "אינו מדבר" },
    { value: "gestures", label: "משתמש בתנועות ידיים וג׳סטות" },
  ],
  vision: [
    { value: "normal", label: "תקינה" },
    { value: "impaired", label: "ידוע על ליקוי ראייה" },
    { value: "glasses_distance", label: "מרכיב משקפיים לראייה מרחוק" },
    { value: "glasses_near", label: "מרכיב משקפיים לראייה מקרוב" },
  ],
  hearing: [
    { value: "normal", label: "תקינה" },
    { value: "impaired", label: "ידוע על ליקוי שמיעה" },
    { value: "aid_left", label: "מרכיב מכשיר שמיעה באוזן שמאל" },
    { value: "aid_right", label: "מרכיב מכשיר שמיעה באוזן ימין" },
    { value: "aid_both", label: "מרכיב מכשיר שמיעה בשתי אוזניים" },
  ],
  functioning: [
    { value: "independent", label: "עצמאי" },
    { value: "light_help", label: "זקוק לסיוע קל בפעולות בודדות" },
    { value: "ongoing_help", label: "זקוק לסיוע בפעולות לאורך זמן" },
    { value: "dependent", label: "תלוי בזולת בכל פעולותיו" },
  ],
  mobility: [
    { value: "independent", label: "עצמאי" },
    { value: "escort", label: "זקוק לליווי" },
    { value: "close_escort", label: "זקוק למלווה צמוד" },
    { value: "position_change", label: "זקוק לסיוע בשינוי תנוחות" },
    { value: "aids", label: "משתמש בעזרים (הליכון, כסא גלגלים, קביים)" },
  ],
  eating: [
    { value: "independent", label: "עצמאי" },
    { value: "light_support", label: "זקוק לתמיכה קלה" },
    { value: "maximal_support", label: "זקוק לתמיכה מרבית" },
  ],
  chewing_swallowing: [
    { value: "no_chewing_difficulty", label: "אין קושי בלעיסה" },
    { value: "no_swallowing_difficulty", label: "אין קושי בבליעה" },
  ],
  food_texture: [
    { value: "not_needed", label: "אין צורך" },
    { value: "chopped", label: "מזון גרוס" },
    { value: "minced", label: "מזון טחון" },
    { value: "thickened_liquids", label: "הסמכת נוזלים" },
  ],
  diet: [
    { value: "regular", label: "רגילה" },
    { value: "low_fat", label: "דלת שומן" },
    { value: "low_sugar", label: "דלת סוכר" },
    { value: "other", label: "אחר" },
  ],
  continence: [
    { value: "full", label: "מלאה" },
    { value: "partial", label: "חלקית" },
    { value: "pull_ups", label: "שימוש במכנסונים" },
    { value: "diapers", label: "שימוש בפנרוס" },
    { value: "catheter_temporary", label: "שימוש בקטטר זמני" },
    { value: "catheter_permanent", label: "שימוש בקטטר קבוע" },
  ],
};

export const SECTIONS: LayoutSection[] = [
  {
    title: "פרטים אישיים",
    items: [
      { kind: "text", key: "phone", label: "טלפון" },
      { kind: "options", key: "lives_with", label: "מתגורר ב" },
    ],
  },
  {
    title: "מידע ונתונים בריאותיים",
    note: "תרופות קבועות ומידע נוסף מפורט במכתב הרפואי המצורף",
    items: [
      {
        kind: "text",
        key: "allergies",
        label: "רגישויות / אלרגיה ידועה",
        multiline: true,
      },
      { kind: "text", key: "known_syndrome", label: "ידוע על תסמונת", multiline: true },
      { kind: "text", key: "background_diseases", label: "מחלות רקע", multiline: true },
      {
        kind: "text",
        key: "hospitalizations_surgeries",
        label: "אשפוזים / ניתוחים בעבר",
        multiline: true,
      },
      { kind: "options", key: "dental_treatment", label: "טיפולי שיניים / חניכיים" },
      { kind: "options", key: "dentures", label: "מערכות שיניים" },
      { kind: "flag", key: "epilepsy_known", label: "ידוע על אפילפסיה" },
      { kind: "text", key: "epilepsy_seizure_nature", label: "אופי התקפים" },
      { kind: "text", key: "epilepsy_seizure_frequency", label: "תדירות התקפים" },
      { kind: "date", key: "epilepsy_last_seizure", label: "התקף אחרון בתאריך" },
      { kind: "text", key: "epilepsy_seizure_treatment", label: "טיפול בזמן התקף" },
      { kind: "flag", key: "dual_diagnosis_known", label: "ידוע על תחלואה כפולה" },
      { kind: "text", key: "dual_diagnosis_expression", label: "מתבטא ב" },
      { kind: "text", key: "dual_diagnosis_frequency", label: "תדירות" },
      { kind: "text", key: "dual_diagnosis_treatment", label: "טיפול שניתן" },
      { kind: "options", key: "skin_integrity", label: "שלמות העור" },
      { kind: "text", key: "skin_known_issues", label: "ידוע על (שלמות העור)" },
    ],
  },
  {
    title: "תפקוד ותקשורת",
    items: [
      { kind: "options", key: "comprehension", label: "הבנה" },
      {
        kind: "options",
        key: "communication",
        label: "שפה ותקשורת",
        other: { key: "communication_other", when: "alternative" },
      },
      { kind: "options", key: "speech", label: "דיבור" },
      { kind: "options", key: "vision", label: "ראייה" },
      { kind: "options", key: "hearing", label: "שמיעה" },
      { kind: "options", key: "functioning", label: "תפקוד" },
      { kind: "options", key: "mobility", label: "ניידות" },
      { kind: "options", key: "eating", label: "אכילה" },
      { kind: "flag", key: "gastrostomy_feeding", label: "האכלה באמצעות גסטרוסטום" },
      { kind: "text", key: "formula", label: "פורמולה" },
      { kind: "options", key: "chewing_swallowing", label: "לעיסה / בליעה" },
      { kind: "options", key: "food_texture", label: "התאמת מרקמי מזון" },
      {
        kind: "options",
        key: "diet",
        label: "דיאטה",
        other: { key: "diet_other", when: "other" },
      },
      { kind: "options", key: "continence", label: "שליטה על סוגרים" },
    ],
  },
  {
    title: "חשוב לדעת",
    items: [
      { kind: "text", key: "loves", label: "דברים שאוהב במיוחד", multiline: true },
      { kind: "text", key: "calming", label: "דברים שמרגיעים אותו", multiline: true },
      { kind: "text", key: "angering", label: "דברים שמכעיסים אותו", multiline: true },
      { kind: "text", key: "frightening", label: "דברים שמפחידים אותו", multiline: true },
      {
        kind: "text",
        key: "stress_behavior",
        label: "מאפייני התנהגות במצבי דחק",
        multiline: true,
      },
      {
        kind: "text",
        key: "care_recommendations",
        label: "המלצות מהצוות הטיפולי הישיר",
        multiline: true,
      },
      { kind: "text", key: "general_notes", label: "הערות כלליות", multiline: true },
    ],
  },
  {
    title: "אנשי קשר וגורמים מטפלים",
    items: [
      { kind: "text", key: "guardian_name", label: "שם אפוטרופוס" },
      { kind: "text", key: "guardian_relation", label: "קרבה" },
      { kind: "text", key: "guardian_phone", label: "טלפון זמין" },
      { kind: "text", key: "health_fund", label: "מבוטח בשירותי בריאות" },
      { kind: "flag", key: "supplemental_insurance", label: "ביטוח רפואי נוסף" },
      { kind: "text", key: "supplemental_insurance_detail", label: "פירוט ביטוח נוסף" },
      { kind: "text", key: "attending_doctor", label: "שם הרופא מנהל הטיפול" },
      { kind: "text", key: "care_nurse", label: "שם האחות מנהלת טיפול" },
      { kind: "text", key: "community_social_worker", label: "עו״ס בקהילה" },
      { kind: "text", key: "social_worker_phone", label: "טלפון עו״ס" },
      { kind: "text", key: "filler_role", label: "תפקיד ממלא הטופס" },
    ],
  },
];

const RESPONSE_ONLY_KEYS: (keyof MedicalSummaryResponse)[] = [
  "student_id",
  "exists",
  "student_name",
  "national_id",
  "date_of_birth",
  "address",
  "written_by_name",
  "updated_at",
];

const SHORT_MAX = 300;
const LONG_MAX = 5000;

export function maxLength(item: { multiline?: boolean }): number {
  return item.multiline ? LONG_MAX : SHORT_MAX;
}

export function toFields(summary: MedicalSummaryResponse): MedicalSummaryFields {
  const fields: Partial<MedicalSummaryResponse> = { ...summary };
  for (const key of RESPONSE_ONLY_KEYS) {
    delete fields[key];
  }
  return fields as MedicalSummaryFields;
}
