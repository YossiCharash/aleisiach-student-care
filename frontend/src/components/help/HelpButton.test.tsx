import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HelpButton } from "@/components/help/HelpButton";
import type { UserResponse, UserRole } from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

async function openHelp(): Promise<void> {
  await userEvent.click(screen.getByRole("button", { name: "עזרה למסך זה" }));
}

describe("HelpButton", () => {
  beforeEach(() => {
    useAuth.mockReset();
  });

  it("renders nothing when there is no signed-in user", () => {
    useAuth.mockReturnValue({ user: null });
    const { container } = render(<HelpButton topic="student" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the manager every section of the student topic", async () => {
    signedInAs("manager");
    render(<HelpButton topic="student" />);
    await openHelp();

    expect(screen.getByText("סיכום עו״ס")).toBeInTheDocument();
    expect(screen.getByText("כתיבת סיכום עו״ס")).toBeInTheDocument();
    expect(screen.getByText("עריכת תוכנית הקידום")).toBeInTheDocument();
    expect(screen.getByText("העברה לארכיון")).toBeInTheDocument();
  });

  it("hides the social-worker note and manager-only actions from a professional teacher", async () => {
    signedInAs("professional_teacher");
    render(<HelpButton topic="student" />);
    await openHelp();

    expect(screen.getByText("דוח תפקודי")).toBeInTheDocument();
    expect(screen.queryByText("סיכום עו״ס")).not.toBeInTheDocument();
    expect(screen.queryByText("פרטי אפוטרופסות ומעמד משפטי")).not.toBeInTheDocument();
    expect(screen.queryByText("עריכת תוכנית הקידום")).not.toBeInTheDocument();
    expect(screen.queryByText("העברה לארכיון")).not.toBeInTheDocument();
  });

  it("shows an instructor the read sections but not manager-only writing", async () => {
    signedInAs("instructor");
    render(<HelpButton topic="student" />);
    await openHelp();

    expect(screen.getByText("סיכום עו״ס")).toBeInTheDocument();
    expect(screen.getByText("פתיחת ישיבת צוות")).toBeInTheDocument();
    expect(screen.queryByText("כתיבת סיכום עו״ס")).not.toBeInTheDocument();
    expect(screen.queryByText("מילוי הדוח התפקודי")).not.toBeInTheDocument();
  });

  it("limits the settings topic to the account section for a non-manager", async () => {
    signedInAs("professional_teacher");
    render(<HelpButton topic="settings" />);
    await openHelp();

    expect(screen.getByText("החשבון שלי")).toBeInTheDocument();
    expect(screen.queryByText("משתמשים")).not.toBeInTheDocument();
    expect(screen.queryByText("סדנאות")).not.toBeInTheDocument();
  });
});
