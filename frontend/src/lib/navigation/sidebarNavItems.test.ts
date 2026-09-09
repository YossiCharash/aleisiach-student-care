import { describe, expect, it } from "vitest";
import type { UserResponse, UserRole } from "@/lib/api/types";
import { sidebarNavItems } from "@/lib/navigation/sidebarNavItems";

function userWith(role: UserRole): UserResponse {
  return { id: "u1", full_name: "מור", role } as UserResponse;
}

function labelsFor(role: UserRole): string[] {
  return sidebarNavItems(userWith(role)).map((item) => item.label);
}

function itemFor(role: UserRole, label: string) {
  const item = sidebarNavItems(userWith(role)).find((entry) => entry.label === label);
  if (!item) {
    throw new Error(`missing nav item ${label}`);
  }
  return item;
}

describe("sidebarNavItems", () => {
  it("gives the super admin the institutions console without student links", () => {
    expect(labelsFor("super_admin")).toEqual(["מוסדות", "הגדרות"]);
  });

  it("gives the manager the archive link", () => {
    expect(labelsFor("manager")).toEqual(["תלמידים", "ארכיון תלמידים", "הגדרות"]);
  });

  it("withholds the archive link from an instructor", () => {
    expect(labelsFor("instructor")).toEqual(["תלמידים", "הגדרות"]);
  });

  it("withholds the archive link from a professional teacher", () => {
    expect(labelsFor("professional_teacher")).toEqual(["תלמידים", "הגדרות"]);
  });

  it("keeps the students link active while viewing one student", () => {
    expect(itemFor("manager", "תלמידים").isActive("/students/abc")).toBe(true);
  });

  it("does not activate the students link on the archive route", () => {
    expect(itemFor("manager", "תלמידים").isActive("/students/archived")).toBe(false);
    expect(itemFor("manager", "ארכיון תלמידים").isActive("/students/archived")).toBe(
      true
    );
  });

  it("activates settings for the account sub-route", () => {
    expect(itemFor("manager", "הגדרות").isActive("/settings?tab=account")).toBe(true);
  });
});
