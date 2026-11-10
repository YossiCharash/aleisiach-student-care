export const queryKeys = {
  students: ["students"] as const,
  archivedStudents: ["students", "archived"] as const,
  student: (studentId: string) => ["students", studentId] as const,
  program: (studentId: string) => ["students", studentId, "program"] as const,
  programPlans: (studentId: string) =>
    ["students", studentId, "program", "plans"] as const,
  meetings: (studentId: string) => ["students", studentId, "meetings"] as const,
  details: (studentId: string) => ["students", studentId, "details"] as const,
  socialNote: (studentId: string) => ["students", studentId, "social-note"] as const,
  functionalReport: (studentId: string) =>
    ["students", studentId, "functional-report"] as const,
  incidentReports: (studentId: string) =>
    ["students", studentId, "incident-reports"] as const,
  riskAssessments: (studentId: string) =>
    ["students", studentId, "risk-assessments"] as const,
  riskResponsibleCandidates: (studentId: string) =>
    ["students", studentId, "risk-assessments", "responsible-candidates"] as const,
  healthRecords: (studentId: string) =>
    ["students", studentId, "health-records"] as const,
  healthResponsibleCandidates: (studentId: string) =>
    ["students", studentId, "health-records", "responsible-candidates"] as const,
  receptionReport: (studentId: string) =>
    ["students", studentId, "reception-report"] as const,
  medicalSummary: (studentId: string) =>
    ["students", studentId, "medical-summary"] as const,
  supportedEmployment: (studentId: string) =>
    ["students", studentId, "supported-employment"] as const,
  taxonomyTree: ["taxonomy", "tree"] as const,
  taxonomyLabels: ["taxonomy", "labels"] as const,
  taxonomySkills: (labelId: string) => ["taxonomy", "skills", labelId] as const,
  taxonomySolutions: (skillId: string) => ["taxonomy", "solutions", skillId] as const,
  users: ["users"] as const,
  workshops: ["workshops"] as const,
  diagnoses: ["diagnoses"] as const,
  riskDomains: ["risk-domains"] as const,
  healthDomains: ["health-domains"] as const,
  detailOptions: ["detail-options"] as const,
  institutions: ["institutions"] as const,
};
