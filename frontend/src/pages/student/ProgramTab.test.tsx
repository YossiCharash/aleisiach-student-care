import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
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
  ProgramForm: () => <div>טופס תוכנית</div>,
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
    {
      skill_id: "sk2",
      skill_name: "צחצוח שיניים",
      rating: "yellow",
      solutions: ["תרגול יומי"],
    },
  ],
};

describe("ProgramTab", () => {
  beforeEach(() => {
    useAuth.mockReset();
    getMock.mockReset();
  });

  it("offers a manager the create button when no program exists", async () => {
    signedInAs("manager");
    getMock.mockResolvedValue(emptyProgram);

    renderWithClient(<ProgramTab studentId="s1" />);

    expect(await screen.findByText("יצירת תוכנית")).toBeInTheDocument();
  });

  it("shows strengths, areas, and the personal plan when a program exists", async () => {
    signedInAs("manager");
    getMock.mockResolvedValue(filledProgram);

    renderWithClient(<ProgramTab studentId="s1" />);

    expect(await screen.findByText("עריכת תוכנית")).toBeInTheDocument();
    expect(screen.getByText("רחיצת ידיים")).toBeInTheDocument();
    expect(screen.getAllByText("צחצוח שיניים").length).toBeGreaterThan(0);
    expect(screen.getByText("תוכנית אישית")).toBeInTheDocument();
    expect(screen.getAllByText("תרגול יומי").length).toBeGreaterThan(0);
  });

  it("hides the edit button from a read-only professional teacher", async () => {
    signedInAs("professional_teacher");
    getMock.mockResolvedValue(filledProgram);

    renderWithClient(<ProgramTab studentId="s1" />);

    expect(await screen.findByText("מוקדי כוח")).toBeInTheDocument();
    expect(screen.queryByText("עריכת תוכנית")).not.toBeInTheDocument();
    expect(screen.queryByText("יצירת תוכנית")).not.toBeInTheDocument();
  });
});
