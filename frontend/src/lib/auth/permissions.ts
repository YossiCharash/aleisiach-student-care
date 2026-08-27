import type { UserResponse } from "@/lib/api/types";

export const permissions = {
  canManage: (user: UserResponse): boolean => user.role === "manager",
  canWriteMeetings: (user: UserResponse): boolean =>
    user.role === "manager" || user.role === "instructor",
  canReadSocialNote: (user: UserResponse): boolean =>
    user.role === "manager" || user.role === "instructor",
  canWriteSocialNote: (user: UserResponse): boolean => user.role === "manager",
  canWriteDetails: (user: UserResponse): boolean =>
    user.role === "manager" || user.role === "instructor",
  canSeeSensitive: (user: UserResponse): boolean => user.role !== "professional_teacher",
  canCreateStudents: (user: UserResponse): boolean => user.role === "manager",
};
