import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import type { UserResponse, UserRole } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { SettingsPage } from "@/pages/SettingsPage";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/pages/settings/UsersArea", () => ({
  UsersArea: () => <div>אזור משתמשים</div>,
}));
vi.mock("@/pages/settings/ClassesArea", () => ({
  ClassesArea: () => <div>אזור כיתות</div>,
}));
vi.mock("@/pages/settings/TaxonomyArea", () => ({
  TaxonomyArea: () => <div>אזור כישורים</div>,
}));
vi.mock("@/pages/settings/DiagnosesArea", () => ({
  DiagnosesArea: () => <div>אזור אבחונים</div>,
}));
vi.mock("@/pages/settings/DetailOptionsArea", () => ({
  DetailOptionsArea: () => <div>אזור פרטי תלמיד</div>,
}));
vi.mock("@/pages/settings/AccountArea", () => ({
  AccountArea: () => <div>אזור החשבון</div>,
}));

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

function renderSettings(path = "/settings"): void {
  renderWithClient(
    <MemoryRouter initialEntries={[path]}>
      <SettingsPage />
    </MemoryRouter>
  );
}

const managerTabs = ["משתמשים", "כיתות", "כישורים", "אבחונים", "עריכת פרטי תלמיד"];

describe("SettingsPage", () => {
  beforeEach(() => useAuth.mockReset());

  it("shows every management tab plus the account tab for a manager", () => {
    signedInAs("manager");
    renderSettings();

    for (const name of [...managerTabs, "החשבון שלי"]) {
      expect(screen.getByRole("tab", { name })).toBeInTheDocument();
    }
    expect(screen.getByText("אזור משתמשים")).toBeInTheDocument();
  });

  it("shows only the account tab for a non-manager", () => {
    signedInAs("professional_teacher");
    renderSettings();

    expect(screen.getByRole("tab", { name: "החשבון שלי" })).toBeInTheDocument();
    for (const name of managerTabs) {
      expect(screen.queryByRole("tab", { name })).not.toBeInTheDocument();
    }
    expect(screen.getByText("אזור החשבון")).toBeInTheDocument();
  });

  it("falls back to the account tab when a non-manager requests a management tab", () => {
    signedInAs("instructor");
    renderSettings("/settings?tab=users");

    expect(screen.getByText("אזור החשבון")).toBeInTheDocument();
    expect(screen.queryByText("אזור משתמשים")).not.toBeInTheDocument();
  });
});
