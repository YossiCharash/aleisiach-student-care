import type { UserRole } from "@/lib/api/types";

export type HelpBlock =
  | { kind: "text"; text: string }
  | { kind: "bullets"; items: string[] }
  | { kind: "steps"; items: string[] }
  | { kind: "callout"; tone: "info" | "tip" | "warn"; title?: string; text: string };

export interface HelpSection {
  id: string;
  title: string;
  roles?: UserRole[];
  blocks: HelpBlock[];
}

export interface HelpTopic {
  title: string;
  intro?: string;
  sections: HelpSection[];
}

export type HelpTopicId =
  | "students"
  | "student"
  | "archived"
  | "settings"
  | "users"
  | "institutions";
