import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { ProgramTab } from "@/pages/student/ProgramTab";
import { programApi } from "@/lib/api/endpoints";
import type { ProgramResponse, UserResponse, UserRole } from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  programApi: { get: vi.fn() },
}));

vi.mock("@/pages/student/program/ProgramForm", () => ({
  ProgramForm: () => <div>טופס מוקדים</div>,
}));

vi.mock("@/pages/student/program/PersonalPlanTab", () => ({
  PersonalPlanTab: () => <div>פאנל תוכנית אישית</div>,
}));

const getMock = vi.mocked(programApi.get);

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

const emptyProgram: ProgramResponse = {
  student_id: "s1",
  exists: false,
  entries: [],
  strengths: [],
  areas_to_strengthen: [],
};

const filledProgram: ProgramResponse = {
  student_id: "s1",
  exists: true,
  entries: [],
  strengths: [{ skill_id: "sk1", skill_name: "רחיצת ידיים" }],
  areas_to_strengthen: [
    { skill_id: "sk2", skill_name: "צחצוח שיניים", rating: "yellow" },
  ],
};

describe("ProgramTab", () => {
  beforeEach(() => {
    useAuth.mockReset();
    getMock.mockReset();
  });

  it("offers a manager the create button when no foci exist", async () => {
    signedInAs("manager");
    getMock.mockResolvedValue(emptyProgram);

    renderWithClient(<ProgramTab studentId="s1" />);

    expect(await screen.findByText("יצירת מוקדים")).toBeInTheDocument();
  });

  it("shows strengths and areas when foci exist", async () => {
    signedInAs("manager");
    getMock.mockResolvedValue(filledProgram);

    renderWithClient(<ProgramTab studentId="s1" />);

    expect(await screen.findByText("עריכת מוקדים")).toBeInTheDocument();
    expect(screen.getByText("רחיצת ידיים")).toBeInTheDocument();
    expect(screen.getByText("צחצוח שיניים")).toBeInTheDocument();
  });

  it("splits the content into a focus sub-tab and a personal-plan sub-tab", async () => {
    signedInAs("manager");
    getMock.mockResolvedValue(filledProgram);

    renderWithClient(<ProgramTab studentId="s1" />);

    expect(
      await screen.findByRole("tab", { name: "מוקדי כוח ומוקדים לחיזוק" })
    ).toBeInTheDocument();
    expect(screen.getByText("מוקדי כוח")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("tab", { name: "תוכנית אישית" }));

    expect(screen.getByText("פאנל תוכנית אישית")).toBeInTheDocument();
    expect(screen.queryByText("מוקדי כוח")).not.toBeInTheDocument();
  });

  it("hides the edit button from a read-only professional teacher", async () => {
    signedInAs("professional_teacher");
    getMock.mockResolvedValue(filledProgram);

    renderWithClient(<ProgramTab studentId="s1" />);

    expect(await screen.findByText("מוקדי כוח")).toBeInTheDocument();
    expect(screen.queryByText("עריכת מוקדים")).not.toBeInTheDocument();
    expect(screen.queryByText("יצירת מוקדים")).not.toBeInTheDocument();
  });
});
