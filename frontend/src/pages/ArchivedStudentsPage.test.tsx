import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import type { ReactElement } from "react";
import { ArchivedStudentsPage } from "@/pages/ArchivedStudentsPage";
import { createTestQueryClient } from "@/test/renderWithClient";
import { studentsApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  studentsApi: { listArchived: vi.fn(), restore: vi.fn() },
}));

const listArchivedMock = vi.mocked(studentsApi.listArchived);
const restoreMock = vi.mocked(studentsApi.restore);

function renderPage(ui: ReactElement): void {
  const client = createTestQueryClient();
  render(
    <QueryClientProvider client={client}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ArchivedStudentsPage", () => {
  beforeEach(() => {
    listArchivedMock.mockReset();
    restoreMock.mockReset();
  });

  it("lists archived students", async () => {
    listArchivedMock.mockResolvedValue([
      { id: "s1", class_id: "c1", full_name: "דנה", is_archived: true },
    ]);

    renderPage(<ArchivedStudentsPage />);

    expect(await screen.findByText("דנה")).toBeInTheDocument();
  });

  it("shows an empty state when the archive is empty", async () => {
    listArchivedMock.mockResolvedValue([]);

    renderPage(<ArchivedStudentsPage />);

    expect(await screen.findByText("אין תלמידים בארכיון.")).toBeInTheDocument();
  });

  it("restores a student via POST /students/{id}/restore", async () => {
    listArchivedMock.mockResolvedValue([
      { id: "s1", class_id: "c1", full_name: "דנה", is_archived: true },
    ]);
    restoreMock.mockResolvedValue({
      id: "s1",
      class_id: "c1",
      full_name: "דנה",
      is_archived: false,
    });

    renderPage(<ArchivedStudentsPage />);
    await screen.findByText("דנה");

    await userEvent.click(screen.getByRole("button", { name: /שחזור/ }));

    await waitFor(() => expect(restoreMock).toHaveBeenCalledWith("s1"));
  });
});
