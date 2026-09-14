import { describe, expect, it } from "vitest";
import { visibleSections } from "@/lib/help/visibleSections";
import type { HelpTopic } from "@/lib/help/types";

const topic: HelpTopic = {
  title: "נושא לדוגמה",
  sections: [
    { id: "everyone", title: "לכולם", blocks: [{ kind: "text", text: "א" }] },
    {
      id: "manager-only",
      title: "למנהל בלבד",
      roles: ["manager"],
      blocks: [{ kind: "text", text: "ב" }],
    },
    {
      id: "staff",
      title: "לצוות המלמד",
      roles: ["manager", "instructor"],
      blocks: [{ kind: "text", text: "ג" }],
    },
  ],
};

describe("visibleSections", () => {
  it("keeps ungated sections for every role", () => {
    const ids = visibleSections(topic, "professional_teacher").map((s) => s.id);
    expect(ids).toContain("everyone");
  });

  it("hides a manager-only section from an instructor", () => {
    const ids = visibleSections(topic, "instructor").map((s) => s.id);
    expect(ids).not.toContain("manager-only");
    expect(ids).toContain("staff");
  });

  it("shows a manager every section", () => {
    const ids = visibleSections(topic, "manager").map((s) => s.id);
    expect(ids).toEqual(["everyone", "manager-only", "staff"]);
  });

  it("hides role-gated sections from a professional teacher", () => {
    const ids = visibleSections(topic, "professional_teacher").map((s) => s.id);
    expect(ids).toEqual(["everyone"]);
  });
});
