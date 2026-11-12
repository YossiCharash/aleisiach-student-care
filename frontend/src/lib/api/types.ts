export type UserRole = "super_admin" | "manager" | "instructor" | "professional_teacher";

export type InvitableRole = Exclude<UserRole, "super_admin">;

export type UserStatus = "invited" | "active" | "disabled";

export type MeetingRating = "green" | "yellow" | "red";

export type LegalStatus = "guardian_appointed" | "parents_are_guardians";

export interface UserResponse {
  id: string;
  full_name: string;
  email: string;
  username: string | null;
  role: UserRole;
  workshop_id: string | null;
  status: UserStatus;
  institution_id: string | null;
}

export interface LoginResponse {
  token: string;
  user: UserResponse;
  institution_name: string | null;
}

export interface InstitutionResponse {
  id: string;
  name: string;
  is_active: boolean;
  contact_name: string | null;
  contact_phone: string | null;
  created_at: string;
}

export interface InstitutionSummary extends InstitutionResponse {
  user_count: number;
  student_count: number;
  pending_manager_email: string | null;
}

export interface InstitutionCreateRequest {
  name: string;
  manager_full_name: string;
  manager_email: string;
  contact_name: string | null;
  contact_phone: string | null;
}

export interface InstitutionUpdateRequest {
  name: string;
  contact_name: string | null;
  contact_phone: string | null;
}

export interface PasswordChangeResponse {
  token: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface InvitationAcceptRequest {
  token: string;
  username: string;
  password: string;
}

export interface InvitationCommand {
  full_name: string;
  email: string;
  role: InvitableRole;
  send_email?: boolean;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirmRequest {
  token: string;
  new_password: string;
}

export interface UserUpdateRequest {
  full_name: string;
  email: string;
  role: UserRole;
}

export interface WorkshopInstructor {
  id: string;
  full_name: string;
}

export interface WorkshopResponse {
  id: string;
  name: string;
  color: string;
  instructors: WorkshopInstructor[];
}

export interface WorkshopUpsertRequest {
  name: string;
  color: string;
  instructor_ids: string[];
}

export interface StudentResponse {
  id: string;
  workshop_id: string;
  full_name: string;
  is_archived: boolean;
}

export interface StudentUpdateRequest {
  full_name: string;
  workshop_id: string;
}

export interface StudentCreateRequest {
  full_name: string;
  workshop_id: string;
  national_id?: string | null;
  date_of_birth?: string | null;
}

export interface SolutionTreeNode {
  id: string;
  text: string;
  rating: MeetingRating;
}

export interface SkillRatings {
  green: string;
  yellow: string;
  red: string;
}

export interface SkillTreeNode {
  id: string;
  name: string;
  green_text: string;
  yellow_text: string;
  red_text: string;
  solutions: SolutionTreeNode[];
}

export interface LabelTreeNode {
  id: string;
  name: string;
  skills: SkillTreeNode[];
}

export interface LabelResponse {
  id: string;
  name: string;
  order: number;
  is_active: boolean;
}

export interface SkillResponse {
  id: string;
  label_id: string;
  name: string;
  order: number;
  is_active: boolean;
  green_text: string;
  yellow_text: string;
  red_text: string;
}

export interface SolutionResponse {
  id: string;
  skill_id: string;
  text: string;
  rating: MeetingRating;
  is_active: boolean;
}

export interface NamedTaxonomyUpdate {
  name?: string;
  is_active?: boolean;
}

export interface SkillUpdate {
  name?: string;
  is_active?: boolean;
  ratings?: SkillRatings;
}

export interface SolutionUpdate {
  text?: string;
  is_active?: boolean;
}

export interface MeetingResponse {
  id: string;
  student_id: string;
  author_id: string;
  meeting_date: string;
  participants: string;
  summary: string;
  created_at: string;
  updated_at: string;
  strengths: ProgramStrength[];
  areas_to_strengthen: ProgramArea[];
  plan_entries: PlanEntryResponse[];
}

export interface MeetingCreateRequest {
  meeting_date: string;
  participants: string;
  summary: string;
}

export interface MeetingUpdateRequest {
  participants: string;
  summary: string;
}

export interface ProgramEntryResponse {
  skill_id: string;
  skill_name_snapshot: string;
  rating: MeetingRating;
}

export interface ProgramStrength {
  skill_id: string;
  skill_name: string;
}

export interface ProgramArea {
  skill_id: string;
  skill_name: string;
  rating: MeetingRating;
}

export interface ProgramResponse {
  student_id: string;
  exists: boolean;
  entries: ProgramEntryResponse[];
  strengths: ProgramStrength[];
  areas_to_strengthen: ProgramArea[];
}

export interface FocusRatingRequest {
  skill_id: string;
  rating: MeetingRating;
}

export interface ProgramUpsertRequest {
  entries: FocusRatingRequest[];
}

export interface PlanSolutionResponse {
  solution_id: string;
  solution_text_snapshot: string;
}

export interface PlanEntryResponse {
  skill_id: string;
  skill_name_snapshot: string;
  rating: MeetingRating;
  solutions: PlanSolutionResponse[];
}

export interface PlanResponse {
  id: string;
  student_id: string;
  author_id: string;
  created_at: string;
  entries: PlanEntryResponse[];
}

export interface PlanEntryRequest {
  skill_id: string;
  solution_ids: string[];
}

export interface PlanCreateRequest {
  entries: PlanEntryRequest[];
}

export type DetailOptionField =
  | "idd_severity"
  | "functioning_level"
  | "medication_independence"
  | "expression_mode"
  | "language_comprehension"
  | "assistive_device"
  | "contact_relationship";

export interface DetailOptionResponse {
  id: string;
  field: DetailOptionField;
  name: string;
  order: number;
  is_active: boolean;
}

export interface DetailOptionUpdate {
  name?: string;
  order?: number;
  is_active?: boolean;
}

export interface DiagnosisCatalogResponse {
  id: string;
  name: string;
  order: number;
  is_active: boolean;
}

export interface DiagnosisCatalogUpdate {
  name?: string;
  order?: number;
  is_active?: boolean;
}

export interface ContactInfo {
  full_name: string;
  relationship: string | null;
  phone: string | null;
}

export interface DiagnosisEntry {
  name: string;
  note: string | null;
}

export interface StudentDetailsResponse {
  student_id: string;
  national_id: string | null;
  date_of_birth: string | null;
  age: number | null;
  address: string | null;
  home_language: string | null;
  idd_severity: string | null;
  functioning_level: string | null;
  additional_diagnoses: DiagnosisEntry[];
  emergency_contacts: ContactInfo[];
  legal_status: LegalStatus | null;
  guardians: ContactInfo[];
  has_allergies_or_dietary: boolean;
  allergies_dietary: string[];
  takes_regular_medication: boolean;
  medications: string[];
  medication_independence: string | null;
  emergency_protocol: string | null;
  assistive_devices: string[];
  assistive_device_other: string | null;
  expression_mode: string | null;
  language_comprehension: string | null;
  previous_institution: string | null;
  prior_task_experience: string | null;
  interests_strengths: string | null;
  triggers: string | null;
  distress_early_signs: string | null;
  calming_methods: string | null;
  sensitive_visible: boolean;
}

export interface StudentDetailsUpsertRequest {
  national_id: string | null;
  date_of_birth: string | null;
  address: string | null;
  home_language: string | null;
  idd_severity: string | null;
  functioning_level: string | null;
  additional_diagnoses: DiagnosisEntry[];
  emergency_contacts: ContactInfo[];
  legal_status: LegalStatus | null;
  guardians: ContactInfo[];
  has_allergies_or_dietary: boolean;
  allergies_dietary: string[];
  takes_regular_medication: boolean;
  medications: string[];
  medication_independence: string | null;
  emergency_protocol: string | null;
  assistive_devices: string[];
  assistive_device_other: string | null;
  expression_mode: string | null;
  language_comprehension: string | null;
  previous_institution: string | null;
  prior_task_experience: string | null;
  interests_strengths: string | null;
  triggers: string | null;
  distress_early_signs: string | null;
  calming_methods: string | null;
}

export interface SocialNoteEntryResponse {
  id: string;
  student_id: string;
  note_date: string;
  content: string;
  author_id: string;
  author_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface SocialNoteReportResponse {
  student_id: string;
  student_name: string;
  entries: SocialNoteEntryResponse[];
}

export interface SocialNoteCreateRequest {
  note_date: string;
  content: string;
}

export interface SocialNoteUpdateRequest {
  content: string;
}

export interface FunctionalReportSections {
  general_background: string;
  vocational_domain: string;
  behavioral_emotional_domain: string;
  communication_social_domain: string;
  independence_life_skills_domain: string;
  summary_recommendations: string;
}

export interface FunctionalReportEntryResponse extends FunctionalReportSections {
  id: string;
  student_id: string;
  report_date: string;
  author_id: string;
  author_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface FunctionalReportHistoryResponse {
  student_id: string;
  student_name: string;
  national_id: string | null;
  date_of_birth: string | null;
  entries: FunctionalReportEntryResponse[];
}

export interface FunctionalReportCreateRequest extends FunctionalReportSections {
  report_date: string;
}

export type IncidentReportType = "internal" | "external";

export type IncidentNature =
  | "accident_injury_death"
  | "violence"
  | "property_damage"
  | "prohibited_substances"
  | "other";

export type IncidentReferral =
  | "internal_event"
  | "guardian"
  | "welfare_social_worker"
  | "statutory_social_worker"
  | "police"
  | "framework_supervisor"
  | "other";

export interface IncidentReportFields {
  event_date: string;
  event_time: string | null;
  location: string;
  reporter_name_role: string;
  report_type: IncidentReportType | null;
  natures: IncidentNature[];
  nature_other: string;
  description: string;
  staff_present: string;
  affected_service_recipients: string;
  warning_signs: string;
  actions_taken: string;
  referrals: IncidentReferral[];
  referral_other: string;
  decision_reasons: string;
  manager_updated_date: string | null;
  manager_updated_time: string | null;
  incident_causes: string;
  was_preventable: string;
  lessons_learned: string;
  corrective_action_plan: string;
  filler_role: string;
}

export interface IncidentReportEntryResponse extends IncidentReportFields {
  id: string;
  student_id: string;
  author_id: string;
  author_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface IncidentReportHistoryResponse {
  student_id: string;
  student_name: string;
  national_id: string | null;
  entries: IncidentReportEntryResponse[];
}

export interface ReceptionChecklistItem {
  done: boolean;
  note: string;
}

export interface ReceptionReportResponse {
  student_id: string;
  exists: boolean;
  student_name: string;
  national_id: string | null;
  date_of_birth: string | null;
  committee_date: string | null;
  committee_participants: string;
  intake_date: string | null;
  committee_summary: string;
  committee_recommendations: string;
  framework_code: string;
  tariff_code: string;
  committee_held: ReceptionChecklistItem;
  director_approval: ReceptionChecklistItem;
  family_guardian_housing_updated: ReceptionChecklistItem;
  community_social_worker_updated: ReceptionChecklistItem;
  management_updated: ReceptionChecklistItem;
  written_by_name: string | null;
  updated_at: string | null;
}

export interface ReceptionReportUpsertRequest {
  committee_date: string | null;
  committee_participants: string;
  intake_date: string | null;
  committee_summary: string;
  committee_recommendations: string;
  framework_code: string;
  tariff_code: string;
  committee_held: ReceptionChecklistItem;
  director_approval: ReceptionChecklistItem;
  family_guardian_housing_updated: ReceptionChecklistItem;
  community_social_worker_updated: ReceptionChecklistItem;
  management_updated: ReceptionChecklistItem;
}

export type WorkStyle = "individual" | "group";

export interface SupportedEmploymentResponse {
  student_id: string;
  exists: boolean;
  workplace: string;
  work_style: WorkStyle | null;
  address: string;
  activity_type: string;
  work_process: string;
  work_environment: string;
  required_body_functions: string;
  hazards_and_safety: string;
  workplace_contact: string;
  escort_contact: string;
  mobility: string;
  work_hours: string;
}

export type SupportedEmploymentUpsertRequest = Omit<
  SupportedEmploymentResponse,
  "student_id" | "exists"
>;

export interface MedicalSummaryFields {
  phone: string;
  lives_with: string[];
  allergies: string;
  known_syndrome: string;
  background_diseases: string;
  hospitalizations_surgeries: string;
  dental_treatment: string[];
  dentures: string[];
  epilepsy_known: boolean | null;
  epilepsy_seizure_nature: string;
  epilepsy_seizure_frequency: string;
  epilepsy_last_seizure: string | null;
  epilepsy_seizure_treatment: string;
  dual_diagnosis_known: boolean | null;
  dual_diagnosis_expression: string;
  dual_diagnosis_frequency: string;
  dual_diagnosis_treatment: string;
  skin_integrity: string[];
  skin_known_issues: string;
  comprehension: string[];
  communication: string[];
  communication_other: string;
  speech: string[];
  vision: string[];
  hearing: string[];
  functioning: string[];
  mobility: string[];
  eating: string[];
  gastrostomy_feeding: boolean | null;
  formula: string;
  chewing_swallowing: string[];
  food_texture: string[];
  diet: string[];
  diet_other: string;
  continence: string[];
  loves: string;
  calming: string;
  angering: string;
  frightening: string;
  stress_behavior: string;
  care_recommendations: string;
  general_notes: string;
  guardian_name: string;
  guardian_relation: string;
  guardian_phone: string;
  health_fund: string;
  supplemental_insurance: boolean | null;
  supplemental_insurance_detail: string;
  attending_doctor: string;
  care_nurse: string;
  community_social_worker: string;
  social_worker_phone: string;
  filler_role: string;
}

export interface MedicalSummaryCreateRequest extends MedicalSummaryFields {
  summary_date: string;
}

export interface MedicalSummaryEntryResponse extends MedicalSummaryFields {
  id: string;
  student_id: string;
  summary_date: string;
  author_id: string;
  author_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface MedicalSummaryHistoryResponse {
  student_id: string;
  student_name: string;
  national_id: string | null;
  date_of_birth: string | null;
  address: string | null;
  entries: MedicalSummaryEntryResponse[];
}

export type RiskLevel = "low" | "medium" | "high" | "not_relevant";

export type RiskCategory = "medical" | "behavioral" | "independence";

export interface RiskDomainInfo {
  id: string;
  category: RiskCategory;
  category_label: string;
  name: string;
  order: number;
  is_active: boolean;
}

export interface RiskDomainUpdate {
  name?: string;
  order?: number;
  is_active?: boolean;
}

export type HealthSessionType = "individual" | "group";

export interface HealthDomainInfo {
  id: string;
  name: string;
  order: number;
  is_active: boolean;
}

export interface HealthRecordRequest {
  domain_id: string;
  record_date: string;
  session_type: HealthSessionType | null;
  support_given: string;
  responsible_user_ids: string[];
  notes: string;
  execution_review: string;
}

export interface HealthRecordResponse extends HealthRecordRequest {
  id: string;
  student_id: string;
  responsible: StaffMember[];
  author_id: string;
  author_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface HealthRecordHistoryResponse {
  student_id: string;
  student_name: string;
  domains: HealthDomainInfo[];
  entries: HealthRecordResponse[];
}

export interface StaffMember {
  id: string;
  full_name: string;
}

export interface RiskItemFields {
  domain_id: string;
  nature: string;
  level: RiskLevel | null;
  intervention_plan: string;
  responsible_user_ids: string[];
}

export interface RiskItemResponse extends RiskItemFields {
  responsible: StaffMember[];
}

export interface RiskAssessmentRequest {
  assessment_date: string;
  items: RiskItemFields[];
}

export interface RiskAssessmentEntryResponse {
  id: string;
  student_id: string;
  assessment_date: string;
  items: RiskItemResponse[];
  author_id: string;
  author_name: string | null;
  created_at: string;
  updated_at: string;
}

export interface RiskAssessmentHistoryResponse {
  student_id: string;
  student_name: string;
  domains: RiskDomainInfo[];
  entries: RiskAssessmentEntryResponse[];
}
