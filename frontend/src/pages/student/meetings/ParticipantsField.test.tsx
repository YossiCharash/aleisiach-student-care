import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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

function staffMember(id: string, fullName: string, role: UserRole): UserResponse {
  return {
    id,
    full_name: fullName,
    email: `${id}@example.com`,
    username: id,
    role,
    workshop_id: null,
    status: "active",
    institution_id: "i1",
  };
}

const instructor: UserResponse = staffMember("u2", "דנה מדריכה", "instructor");
const manager: UserResponse = staffMember("u3", "רוני מנהלת", "manager");
const teacher: UserResponse = staffMember("u4", "גיל מורה", "professional_teacher");
const disabledManager: UserResponse = {
  ...staffMember("u5", "עדי לשעבר", "manager"),
  status: "disabled",
};

function signedInAs(role: UserRole): void {
  useAuth.mockReturnValue({ user: { id: "u1", full_name: "מור", role } });
}

async function openStaffDropdown(): Promise<ReturnType<typeof userEvent.setup>> {
  const user = userEvent.setup();
  await user.click(await screen.findByRole("button", { name: "בחירת משתתפים מהצוות" }));
  return user;
}

describe("ParticipantsField", () => {
  beforeEach(() => {
    useAuth.mockReset();
    usersMock.mockReset();
    usersMock.mockResolvedValue([instructor, manager, teacher, disabledManager]);
  });

  it("lists active managers and instructors in the staff dropdown", async () => {
    signedInAs("manager");
    renderWithClient(
      <ParticipantsField id="participants" value="" onChange={() => {}} />
    );

    await openStaffDropdown();

    expect(
      screen.getByRole("menuitemcheckbox", { name: "דנה מדריכה" })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("menuitemcheckbox", { name: "רוני מנהלת" })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("menuitemcheckbox", { name: "גיל מורה" })
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("menuitemcheckbox", { name: "עדי לשעבר" })
    ).not.toBeInTheDocument();
  });

  it("lists a name shared by two staff members once", async () => {
    signedInAs("manager");
    usersMock.mockResolvedValue([instructor, staffMember("u6", "דנה מדריכה", "manager")]);
    renderWithClient(
      <ParticipantsField id="participants" value="" onChange={() => {}} />
    );

    await openStaffDropdown();

    expect(screen.getAllByRole("menuitemcheckbox", { name: "דנה מדריכה" })).toHaveLength(
      1
    );
  });

  it("appends a checked staff member to the typed names", async () => {
    signedInAs("manager");
    const onChange = vi.fn();
    renderWithClient(
      <ParticipantsField id="participants" value="אורח" onChange={onChange} />
    );

    const user = await openStaffDropdown();
    await user.click(screen.getByRole("menuitemcheckbox", { name: "רוני מנהלת" }));

    expect(onChange).toHaveBeenCalledWith("אורח, רוני מנהלת");
  });

  it("marks listed staff as checked and removes them when unchecked", async () => {
    signedInAs("manager");
    const onChange = vi.fn();
    renderWithClient(
      <ParticipantsField id="participants" value="דנה מדריכה, אורח" onChange={onChange} />
    );

    const user = await openStaffDropdown();
    const dana = screen.getByRole("menuitemcheckbox", { name: "דנה מדריכה" });
    expect(dana).toHaveAttribute("aria-checked", "true");
    await user.click(dana);

    expect(onChange).toHaveBeenCalledWith("אורח");
  });

  it("shows no staff dropdown for a non-manager instructor", async () => {
    signedInAs("instructor");
    renderWithClient(
      <ParticipantsField id="participants" value="" onChange={() => {}} />
    );

    await screen.findByLabelText("משתתפים");
    expect(
      screen.queryByRole("button", { name: "בחירת משתתפים מהצוות" })
    ).not.toBeInTheDocument();
    expect(usersMock).not.toHaveBeenCalled();
  });
});
