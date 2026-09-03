import { describe, expect, it } from "vitest";
import { displayName } from "@/lib/auth/displayName";
import type { UserResponse } from "@/lib/api/types";

const baseUser: UserResponse = {
  id: "u1",
  full_name: "מור כהן",
  email: "mor@example.com",
  username: "mor.c",
  role: "instructor",
  class_id: "c1",
  status: "active",
  institution_id: "i1",
};

describe("displayName", () => {
  it("prefers the username the user chose", () => {
    expect(displayName(baseUser)).toBe("mor.c");
  });

  it("falls back to the manager-provided full name before the invitation is accepted", () => {
    expect(displayName({ ...baseUser, username: null, status: "invited" })).toBe(
      "מור כהן"
    );
  });
});
