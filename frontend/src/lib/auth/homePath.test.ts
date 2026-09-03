import { describe, expect, it } from "vitest";
import { homePath } from "@/lib/auth/homePath";
import type { UserResponse, UserRole } from "@/lib/api/types";

function userWithRole(role: UserRole): UserResponse {
  return {
    id: "u1",
    full_name: "בודק",
    email: "test@example.com",
    username: "tester",
    role,
    class_id: null,
    status: "active",
    institution_id: role === "super_admin" ? null : "i1",
  };
}

describe("homePath", () => {
  it("sends a super admin to the institutions console", () => {
    expect(homePath(userWithRole("super_admin"))).toBe("/institutions");
  });

  it("sends institution users to the student list", () => {
    expect(homePath(userWithRole("manager"))).toBe("/");
    expect(homePath(userWithRole("instructor"))).toBe("/");
    expect(homePath(userWithRole("professional_teacher"))).toBe("/");
  });

  it("falls back to the student list when there is no user", () => {
    expect(homePath(null)).toBe("/");
  });
});
