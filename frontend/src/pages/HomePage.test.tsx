import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import type { UserResponse, UserRole } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { HomePage } from "@/pages/HomePage";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

function renderHome(): void {
  renderWithClient(
    <MemoryRouter initialEntries={["/"]}>
      <HomePage />
    </MemoryRouter>
  );
}

describe("HomePage", () => {
  beforeEach(() => useAuth.mockReset());

  it("offers the manager students, classes and meetings", () => {
    signedInAs("manager");
    renderHome();

    expect(screen.getByRole("link", { name: /^תלמידים/ })).toHaveAttribute(
      "href",
      "/students"
    );
    expect(screen.getByRole("link", { name: /^כיתות/ })).toHaveAttribute("href", "/classes");
    expect(screen.getByRole("link", { name: /^ישיבות צוות/ })).toHaveAttribute(
      "href",
      "/meetings"
    );
  });

  it("hides the classes hub from a non-manager", () => {
    signedInAs("professional_teacher");
    renderHome();

    expect(screen.getByRole("link", { name: /^תלמידים/ })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^ישיבות צוות/ })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /^כיתות/ })).not.toBeInTheDocument();
  });
});
