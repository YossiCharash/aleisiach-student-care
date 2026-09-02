import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
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
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/students" element={<div>רשימת התלמידים</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("HomePage", () => {
  beforeEach(() => useAuth.mockReset());

  it("offers the manager students, settings and archive", () => {
    signedInAs("manager");
    renderHome();

    expect(screen.getByRole("link", { name: /^תלמידים/ })).toHaveAttribute(
      "href",
      "/students"
    );
    expect(screen.getByRole("link", { name: /^הגדרות/ })).toHaveAttribute(
      "href",
      "/settings"
    );
    expect(screen.getByRole("link", { name: /^ארכיון/ })).toHaveAttribute(
      "href",
      "/students/archived"
    );
  });

  it("greets the manager by name", () => {
    signedInAs("manager");
    renderHome();

    expect(screen.getByRole("heading", { name: "שלום מור" })).toBeInTheDocument();
  });

  it("sends an instructor straight to the student list", () => {
    signedInAs("instructor");
    renderHome();

    expect(screen.getByText("רשימת התלמידים")).toBeInTheDocument();
  });

  it("sends a professional teacher straight to the student list", () => {
    signedInAs("professional_teacher");
    renderHome();

    expect(screen.getByText("רשימת התלמידים")).toBeInTheDocument();
  });
});
