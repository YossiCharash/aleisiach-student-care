import type {
  HealthRecordRequest,
  HealthRecordResponse,
  HealthSessionType,
} from "@/lib/api/types";

export const HEALTH_TITLE = "תיעוד אישי – מקצועות הבריאות";

export const HEALTH_COLUMNS = [
  "תאריך",
  "אישי/קבוצתי",
  "תמיכה שניתנה",
  "אחראי ביצוע",
  "הערות",
  "בקרת ביצוע",
] as const;

export const SESSION_TYPES: { value: HealthSessionType; label: string }[] = [
  { value: "individual", label: "אישי" },
  { value: "group", label: "קבוצתי" },
];

export function sessionTypeLabel(value: HealthSessionType | null): string {
  return SESSION_TYPES.find((option) => option.value === value)?.label ?? "";
}

export function emptyRecord(domainId: string, recordDate: string): HealthRecordRequest {
  return {
    domain_id: domainId,
    record_date: recordDate,
    session_type: null,
    support_given: "",
    responsible_user_ids: [],
    notes: "",
    execution_review: "",
  };
}

export function requestOf(record: HealthRecordResponse): HealthRecordRequest {
  return {
    domain_id: record.domain_id,
    record_date: record.record_date,
    session_type: record.session_type,
    support_given: record.support_given,
    responsible_user_ids: record.responsible_user_ids,
    notes: record.notes,
    execution_review: record.execution_review,
  };
}

export function hasContent(request: HealthRecordRequest): boolean {
  return (
    request.session_type !== null ||
    request.support_given.trim() !== "" ||
    request.responsible_user_ids.length > 0 ||
    request.notes.trim() !== "" ||
    request.execution_review.trim() !== ""
  );
}
