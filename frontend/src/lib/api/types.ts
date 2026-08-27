export type UserRole = "manager" | "instructor" | "professional_teacher";

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
}

export interface LoginResponse {
  token: string;
  user: UserResponse;
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
  role: UserRole;
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

export interface StudentCreateRequest {
  full_name: string;
  class_id: string;
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

export interface MeetingEntryRequest {
  skill_id: string;
  rating: MeetingRating;
  solution_ids: string[];
}

export interface MeetingCreateRequest {
  year: number;
  month: number;
  entries: MeetingEntryRequest[];
}

export interface ProgramStrength {
  skill_id: string;
  skill_name: string;
  year: number;
  month: number;
}

export interface ProgramArea {
  skill_id: string;
  skill_name: string;
  rating: MeetingRating;
  solutions: string[];
  year: number;
  month: number;
}

export interface ProgramResponse {
  student_id: string;
  strengths: ProgramStrength[];
  areas_to_strengthen: ProgramArea[];
}

export interface Diagnosis {
  name: string;
  notes: string | null;
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
  medical_diagnoses: Diagnosis[];
  emergency_contacts: ContactInfo[];
  legal_status: LegalStatus | null;
  guardians: ContactInfo[];
  sensitive_visible: boolean;
}

export interface StudentDetailsUpsertRequest {
  national_id: string | null;
  date_of_birth: string | null;
  address: string | null;
  home_language: string | null;
  medical_diagnoses: Diagnosis[];
  emergency_contacts: ContactInfo[];
  legal_status: LegalStatus | null;
  guardians: ContactInfo[];
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
