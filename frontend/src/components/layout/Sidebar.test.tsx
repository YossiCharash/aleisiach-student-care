import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import type { UserResponse, UserRole } from "@/lib/api/types";
import { renderWithClient } from "@/test/renderWithClient";
import { Sidebar } from "@/components/layout/Sidebar";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

const logout = vi.fn();

function signedInAs(
  role: UserRole,
  institutionName: string | null = "מרכז עלי שיח"
): void {
  const user: Partial<UserResponse> = {
    id: "u1",
    full_name: "רונית כהן",
    username: "ronit",
    role,
  };
  useAuth.mockReturnValue({ user, institutionName, logout });
}

function renderSidebar(path = "/students"): void {
  renderWithClient(
    <MemoryRouter initialEntries={[path]}>
      <Sidebar />
    </MemoryRouter>
  );
}

describe("Sidebar", () => {
  beforeEach(() => {
    useAuth.mockReset();
    logout.mockReset();
  });

  it("renders nothing when signed out", () => {
    useAuth.mockReturnValue({ user: null, institutionName: null, logout });
    const { container } = renderWithClient(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("shows the institution name and the signed-in user", () => {
    signedInAs("manager");
    renderSidebar();

    expect(screen.getByText("מרכז עלי שיח")).toBeInTheDocument();
    expect(screen.getByText("ronit")).toBeInTheDocument();
    expect(screen.getByText("מנהל/ת")).toBeInTheDocument();
  });

  it("marks the current route as the active nav item", () => {
    signedInAs("manager");
    renderSidebar("/students/archived");

    expect(screen.getByRole("link", { name: "ארכיון תלמידים" })).toHaveAttribute(
      "aria-current",
      "page"
    );
    expect(screen.getByRole("link", { name: "תלמידים" })).not.toHaveAttribute(
      "aria-current"
    );
  });

  it("shows the institutions console for a super admin instead of students", () => {
    signedInAs("super_admin", null);
    renderSidebar("/institutions");

    expect(screen.getByRole("link", { name: "מוסדות" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "תלמידים" })).not.toBeInTheDocument();
    expect(screen.getByText("ניהול מוסדות")).toBeInTheDocument();
  });

  it("logs the user out", async () => {
    signedInAs("instructor");
    renderSidebar();

    await userEvent.click(screen.getByRole("button", { name: "יציאה" }));

    await waitFor(() => expect(logout).toHaveBeenCalledOnce());
  });
});
