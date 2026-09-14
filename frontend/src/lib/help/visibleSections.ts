import type { UserRole } from "@/lib/api/types";
import type { HelpSection, HelpTopic } from "@/lib/help/types";

export function visibleSections(topic: HelpTopic, role: UserRole): HelpSection[] {
  return topic.sections.filter(
    (section) => section.roles === undefined || section.roles.includes(role)
  );
}
