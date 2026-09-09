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
  class_id: string | null;
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
  code: string;
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
  code: string;
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
  class_id: string | null;
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
  class_id: string | null;
}

export interface ClassResponse {
  id: string;
  name: string;
}

export interface StudentResponse {
  id: string;
  class_id: string;
  full_name: string;
  is_archived: boolean;
}

export interface StudentUpdateRequest {
  full_name: string;
  class_id: string;
}

export interface StudentCreateRequest {
  full_name: string;
  class_id: string;
  national_id?: string | null;
  date_of_birth?: string | null;
}

export interface SolutionTreeNode {
  id: string;
  text: string;
}

export interface SkillTreeNode {
  id: string;
  name: string;
  solutions: SolutionTreeNode[];
}

export interface SubLabelTreeNode {
  id: string;
  name: string;
  skills: SkillTreeNode[];
}

export interface LabelTreeNode {
  id: string;
  name: string;
  sub_labels: SubLabelTreeNode[];
}

export interface LabelResponse {
  id: string;
  name: string;
  order: number;
  is_active: boolean;
}

export interface SubLabelResponse {
  id: string;
  label_id: string;
  name: string;
  order: number;
  is_active: boolean;
}

export interface SkillResponse {
  id: string;
  sub_label_id: string;
  name: string;
  order: number;
  is_active: boolean;
}

export interface SolutionResponse {
  id: string;
  skill_id: string;
  text: string;
  is_active: boolean;
}

export interface NamedTaxonomyUpdate {
  name?: string;
  is_active?: boolean;
}

export interface SolutionUpdate {
  text?: string;
  is_active?: boolean;
}

export interface MeetingEntrySolutionResponse {
  id: string;
  solution_id: string;
  solution_text_snapshot: string;
}

export interface MeetingEntryResponse {
  id: string;
  skill_id: string;
  skill_name_snapshot: string;
  rating: MeetingRating;
  solutions: MeetingEntrySolutionResponse[];
}

export interface MeetingResponse {
  id: string;
  student_id: string;
  year: number;
  month: number;
  author_id: string;
  created_at: string;
  entries: MeetingEntryResponse[];
}

export interface SkillRatingRequest {
  skill_id: string;
  rating: MeetingRating;
  solution_ids: string[];
}

export interface MeetingCreateRequest {
  year: number;
  month: number;
  entries: SkillRatingRequest[];
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
  | "disability_severity"
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

export interface StudentDetailsResponse {
  student_id: string;
  national_id: string | null;
  date_of_birth: string | null;
  age: number | null;
  address: string | null;
  home_language: string | null;
  idd_severity: string | null;
  disability_severity: string | null;
  functioning_level: string | null;
  additional_diagnoses: string[];
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
  current_institution: string | null;
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
  disability_severity: string | null;
  functioning_level: string | null;
  additional_diagnoses: string[];
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
  current_institution: string | null;
  prior_task_experience: string | null;
  interests_strengths: string | null;
  triggers: string | null;
  distress_early_signs: string | null;
  calming_methods: string | null;
}

export interface SocialNoteResponse {
  student_id: string;
  content: string | null;
  updated_by: string | null;
  updated_at: string | null;
}

export interface SocialNoteUpsertRequest {
  content: string;
}

export interface FunctionalReportResponse {
  student_id: string;
  exists: boolean;
  student_name: string;
  national_id: string | null;
  date_of_birth: string | null;
  general_background: string;
  vocational_domain: string;
  behavioral_emotional_domain: string;
  communication_social_domain: string;
  independence_life_skills_domain: string;
  summary_recommendations: string;
  written_by_name: string | null;
  updated_at: string | null;
}

export interface FunctionalReportUpsertRequest {
  general_background: string;
  vocational_domain: string;
  behavioral_emotional_domain: string;
  communication_social_domain: string;
  independence_life_skills_domain: string;
  summary_recommendations: string;
}
