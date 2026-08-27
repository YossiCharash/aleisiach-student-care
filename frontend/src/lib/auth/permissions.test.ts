import { describe, expect, it } from "vitest";
import { permissions } from "@/lib/auth/permissions";
import type { UserResponse, UserRole } from "@/lib/api/types";

function userWithRole(role: UserRole): UserResponse {
  return {
    id: "user-id",
    full_name: "בדיקה",
    email: "test@example.com",
    username: "tester",
    role,
    class_id: null,
    status: "active",
  };
}

const manager = userWithRole("manager");
const instructor = userWithRole("instructor");
const teacher = userWithRole("professional_teacher");

describe("permissions matrix", () => {
  it("only the manager manages settings and creates students", () => {
    expect(permissions.canManage(manager)).toBe(true);
    expect(permissions.canManage(instructor)).toBe(false);
    expect(permissions.canCreateStudents(teacher)).toBe(false);
  });

  it("manager and instructor may write meetings; teacher may not", () => {
    expect(permissions.canWriteMeetings(manager)).toBe(true);
    expect(permissions.canWriteMeetings(instructor)).toBe(true);
    expect(permissions.canWriteMeetings(teacher)).toBe(false);
  });

  it("only the manager writes the social note; the teacher cannot read it", () => {
    expect(permissions.canWriteSocialNote(manager)).toBe(true);
    expect(permissions.canWriteSocialNote(instructor)).toBe(false);
    expect(permissions.canReadSocialNote(teacher)).toBe(false);
  });

  it("the professional teacher never sees sensitive data", () => {
    expect(permissions.canSeeSensitive(manager)).toBe(true);
    expect(permissions.canSeeSensitive(instructor)).toBe(true);
    expect(permissions.canSeeSensitive(teacher)).toBe(false);
  });
});
