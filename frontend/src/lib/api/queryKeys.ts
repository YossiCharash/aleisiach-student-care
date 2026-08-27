export const queryKeys = {
  students: ["students"] as const,
  archivedStudents: ["students", "archived"] as const,
  student: (studentId: string) => ["students", studentId] as const,
  program: (studentId: string) => ["students", studentId, "program"] as const,
  meetings: (studentId: string) => ["students", studentId, "meetings"] as const,
  details: (studentId: string) => ["students", studentId, "details"] as const,
  socialNote: (studentId: string) => ["students", studentId, "social-note"] as const,
  taxonomyTree: ["taxonomy", "tree"] as const,
  taxonomyLabels: ["taxonomy", "labels"] as const,
  users: ["users"] as const,
  classes: ["classes"] as const,
};
