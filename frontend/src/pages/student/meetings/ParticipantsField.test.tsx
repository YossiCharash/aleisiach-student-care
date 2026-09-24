import { describe, expect, it, vi, beforeEach } from "vitest";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { ParticipantsField } from "@/pages/student/meetings/ParticipantsField";
import { usersApi } from "@/lib/api/endpoints";
import type { UserResponse, UserRole } from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  usersApi: { list: vi.fn() },
}));

const usersMock = vi.mocked(usersApi.list);

const instructor: UserResponse = {
  id: "u2",
  full_name: "דנה מדריכה",
  email: "dana@example.com",
  username: "dana",
  role: "instructor",
  workshop_id: null,
  status: "active",
  institution_id: "i1",
};

function signedInAs(role: UserRole): void {
  useAuth.mockReturnValue({ user: { id: "u1", full_name: "מור", role } });
}

describe("ParticipantsField", () => {
  beforeEach(() => {
    useAuth.mockReset();
    usersMock.mockReset();
    usersMock.mockResolvedValue([instructor]);
  });

  it("lets a manager append an instructor name by clicking its chip", async () => {
    signedInAs("manager");
    const onChange = vi.fn();
    renderWithClient(
      <ParticipantsField id="participants" value="" onChange={onChange} />
    );

    fireEvent.click(await screen.findByRole("button", { name: "דנה מדריכה" }));

    expect(onChange).toHaveBeenCalledWith("דנה מדריכה");
  });

  it("does not duplicate an already-listed instructor", async () => {
    signedInAs("manager");
    const onChange = vi.fn();
    renderWithClient(
      <ParticipantsField id="participants" value="דנה מדריכה" onChange={onChange} />
    );

    fireEvent.click(await screen.findByRole("button", { name: "דנה מדריכה" }));

    expect(onChange).toHaveBeenCalledWith("דנה מדריכה");
  });

  it("shows no instructor chips for a non-manager instructor", async () => {
    signedInAs("instructor");
    renderWithClient(
      <ParticipantsField id="participants" value="" onChange={() => {}} />
    );

    await screen.findByLabelText("משתתפים");
    expect(screen.queryByRole("button", { name: "דנה מדריכה" })).not.toBeInTheDocument();
    expect(usersMock).not.toHaveBeenCalled();
  });
});
