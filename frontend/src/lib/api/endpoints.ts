import { apiClient, buildPdfUrl } from "@/lib/api/client";
import type {
  InvitationCommand,
  LabelResponse,
  LabelTreeNode,
  LoginRequest,
  LoginResponse,
  MeetingCreateRequest,
  MeetingResponse,
  NamedTaxonomyUpdate,
  ProgramResponse,
  SkillResponse,
  SocialNoteResponse,
  SocialNoteUpsertRequest,
  SolutionResponse,
  SolutionUpdate,
  StudentCreateRequest,
  StudentDetailsResponse,
  StudentDetailsUpsertRequest,
  StudentResponse,
  SubLabelResponse,
  UserResponse,
} from "@/lib/api/types";

export const authApi = {
  login: (body: LoginRequest): Promise<LoginResponse> =>
    apiClient.postPublic<LoginResponse>("/auth/login", body),
  logout: (): Promise<void> => apiClient.post<void>("/auth/logout"),
  acceptInvitation: (body: { token: string; username: string; password: string }): Promise<UserResponse> =>
    apiClient.postPublic<UserResponse>("/auth/invitations/accept", body),
  requestPasswordReset: (email: string): Promise<void> =>
    apiClient.postPublic<void>("/auth/password-reset/request", { email }),
  confirmPasswordReset: (token: string, newPassword: string): Promise<void> =>
    apiClient.postPublic<void>("/auth/password-reset/confirm", {
      token,
      new_password: newPassword,
    }),
  createInvitation: (body: InvitationCommand): Promise<UserResponse> =>
    apiClient.post<UserResponse>("/auth/invitations", body),
};

export const usersApi = {
  list: (): Promise<UserResponse[]> => apiClient.get<UserResponse[]>("/users"),
  disable: (userId: string): Promise<UserResponse> =>
    apiClient.post<UserResponse>(`/users/${userId}/disable`),
  enable: (userId: string): Promise<UserResponse> =>
    apiClient.post<UserResponse>(`/users/${userId}/enable`),
};

export const studentsApi = {
  list: (): Promise<StudentResponse[]> => apiClient.get<StudentResponse[]>("/students"),
  get: (studentId: string): Promise<StudentResponse> =>
    apiClient.get<StudentResponse>(`/students/${studentId}`),
  create: (body: StudentCreateRequest): Promise<StudentResponse> =>
    apiClient.post<StudentResponse>("/students", body),
  archive: (studentId: string): Promise<StudentResponse> =>
    apiClient.post<StudentResponse>(`/students/${studentId}/archive`),
};

export const programApi = {
  get: (studentId: string): Promise<ProgramResponse> =>
    apiClient.get<ProgramResponse>(`/students/${studentId}/program`),
};

export const meetingsApi = {
  list: (studentId: string): Promise<MeetingResponse[]> =>
    apiClient.get<MeetingResponse[]>(`/students/${studentId}/meetings`),
  get: (studentId: string, meetingId: string): Promise<MeetingResponse> =>
    apiClient.get<MeetingResponse>(`/students/${studentId}/meetings/${meetingId}`),
  create: (studentId: string, body: MeetingCreateRequest): Promise<MeetingResponse> =>
    apiClient.post<MeetingResponse>(`/students/${studentId}/meetings`, body),
  pdfUrl: (studentId: string, meetingId: string): string =>
    buildPdfUrl(`/students/${studentId}/meetings/${meetingId}/pdf`),
};

export const detailsApi = {
  get: (studentId: string): Promise<StudentDetailsResponse> =>
    apiClient.get<StudentDetailsResponse>(`/students/${studentId}/details`),
  upsert: (studentId: string, body: StudentDetailsUpsertRequest): Promise<StudentDetailsResponse> =>
    apiClient.put<StudentDetailsResponse>(`/students/${studentId}/details`, body),
  pdfUrl: (studentId: string): string => buildPdfUrl(`/students/${studentId}/details/pdf`),
};

export const socialNoteApi = {
  get: (studentId: string): Promise<SocialNoteResponse> =>
    apiClient.get<SocialNoteResponse>(`/students/${studentId}/social-note`),
  upsert: (studentId: string, body: SocialNoteUpsertRequest): Promise<SocialNoteResponse> =>
    apiClient.put<SocialNoteResponse>(`/students/${studentId}/social-note`, body),
};

export const taxonomyApi = {
  tree: (): Promise<LabelTreeNode[]> => apiClient.get<LabelTreeNode[]>("/taxonomy/tree"),
  listLabels: (includeInactive = false): Promise<LabelResponse[]> =>
    apiClient.get<LabelResponse[]>(`/taxonomy/labels?include_inactive=${includeInactive}`),
  createLabel: (name: string): Promise<LabelResponse> =>
    apiClient.post<LabelResponse>("/taxonomy/labels", { name }),
  createSubLabel: (labelId: string, name: string): Promise<SubLabelResponse> =>
    apiClient.post<SubLabelResponse>("/taxonomy/sub-labels", { label_id: labelId, name }),
  createSkill: (subLabelId: string, name: string): Promise<SkillResponse> =>
    apiClient.post<SkillResponse>("/taxonomy/skills", { sub_label_id: subLabelId, name }),
  createSolution: (skillId: string, text: string): Promise<SolutionResponse> =>
    apiClient.post<SolutionResponse>("/taxonomy/solutions", { skill_id: skillId, text }),
  updateLabel: (labelId: string, body: NamedTaxonomyUpdate): Promise<LabelResponse> =>
    apiClient.patch<LabelResponse>(`/taxonomy/labels/${labelId}`, body),
  updateSubLabel: (subLabelId: string, body: NamedTaxonomyUpdate): Promise<SubLabelResponse> =>
    apiClient.patch<SubLabelResponse>(`/taxonomy/sub-labels/${subLabelId}`, body),
  updateSkill: (skillId: string, body: NamedTaxonomyUpdate): Promise<SkillResponse> =>
    apiClient.patch<SkillResponse>(`/taxonomy/skills/${skillId}`, body),
  updateSolution: (solutionId: string, body: SolutionUpdate): Promise<SolutionResponse> =>
    apiClient.patch<SolutionResponse>(`/taxonomy/solutions/${solutionId}`, body),
};
