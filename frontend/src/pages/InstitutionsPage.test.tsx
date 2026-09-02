import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { InstitutionsPage } from "@/pages/InstitutionsPage";
import { createTestQueryClient } from "@/test/renderWithClient";
import { institutionsApi } from "@/lib/api/endpoints";
import type { InstitutionSummary } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  institutionsApi: {
    list: vi.fn(),
    create: vi.fn(),
    rename: vi.fn(),
    deactivate: vi.fn(),
    activate: vi.fn(),
  },
}));

const listMock = vi.mocked(institutionsApi.list);
const createMock = vi.mocked(institutionsApi.create);
const deactivateMock = vi.mocked(institutionsApi.deactivate);

function institution(overrides: Partial<InstitutionSummary> = {}): InstitutionSummary {
  return {
    id: "i1",
    name: "בית ספר אלף",
    code: "alef",
    is_active: true,
    created_at: "2026-09-01T00:00:00Z",
    user_count: 4,
    student_count: 12,
    ...overrides,
  };
}

function renderPage(ui: ReactElement): void {
  render(
    <QueryClientProvider client={createTestQueryClient()}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("InstitutionsPage", () => {
  beforeEach(() => {
    listMock.mockReset();
    createMock.mockReset();
    deactivateMock.mockReset();
  });

  it("lists institutions with their user and student counts", async () => {
    listMock.mockResolvedValue([institution()]);

    renderPage(<InstitutionsPage />);

    expect(await screen.findByText("בית ספר אלף")).toBeInTheDocument();
    expect(screen.getByText("alef")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("shows an empty state when no institution exists yet", async () => {
    listMock.mockResolvedValue([]);

    renderPage(<InstitutionsPage />);

    expect(await screen.findByText("עדיין לא הוקם אף מוסד.")).toBeInTheDocument();
  });

  it("marks a deactivated institution", async () => {
    listMock.mockResolvedValue([institution({ is_active: false })]);

    renderPage(<InstitutionsPage />);

    expect(await screen.findByText("מושבת")).toBeInTheDocument();
  });

  it("creates an institution together with its first manager", async () => {
    listMock.mockResolvedValue([]);
    createMock.mockResolvedValue({
      id: "i2",
      name: "בית ספר בית",
      code: "bet",
      is_active: true,
      created_at: "2026-09-02T00:00:00Z",
    });

    renderPage(<InstitutionsPage />);
    await screen.findByText("עדיין לא הוקם אף מוסד.");

    await userEvent.click(screen.getByRole("button", { name: /מוסד חדש/ }));
    await userEvent.type(screen.getByLabelText("שם המוסד"), "בית ספר בית");
    await userEvent.type(screen.getByLabelText("קוד המוסד"), "bet");
    await userEvent.type(screen.getByLabelText("שם מנהל/ת המוסד"), "רותי");
    await userEvent.type(screen.getByLabelText("דוא״ל מנהל/ת המוסד"), "ruti@example.org");
    await userEvent.click(screen.getByRole("button", { name: "הקמת המוסד" }));

    await waitFor(() =>
      expect(createMock).toHaveBeenCalledWith({
        name: "בית ספר בית",
        code: "bet",
        manager_full_name: "רותי",
        manager_email: "ruti@example.org",
      })
    );
  });

  it("asks for confirmation before deactivating an institution", async () => {
    listMock.mockResolvedValue([institution()]);
    deactivateMock.mockResolvedValue({
      id: "i1",
      name: "בית ספר אלף",
      code: "alef",
      is_active: false,
      created_at: "2026-09-01T00:00:00Z",
    });

    renderPage(<InstitutionsPage />);
    await screen.findByText("בית ספר אלף");

    await userEvent.click(screen.getByRole("button", { name: "השבתת המוסד" }));
    expect(deactivateMock).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "השבתה" }));

    await waitFor(() => expect(deactivateMock).toHaveBeenCalledWith("i1"));
  });
});
