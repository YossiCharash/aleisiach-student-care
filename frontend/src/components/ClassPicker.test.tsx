import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ClassPicker } from "@/components/ClassPicker";
import { renderWithClient } from "@/test/renderWithClient";
import { classesApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  classesApi: { list: vi.fn() },
}));

const listMock = vi.mocked(classesApi.list);

describe("ClassPicker", () => {
  beforeEach(() => {
    listMock.mockReset();
  });

  it("loads classes from the server and renders them as options", async () => {
    listMock.mockResolvedValue([
      { id: "c1", name: "כיתה א" },
      { id: "c2", name: "כיתה ב" },
    ]);

    renderWithClient(<ClassPicker id="class" value="" onChange={() => {}} />);

    expect(await screen.findByRole("option", { name: "כיתה א" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "כיתה ב" })).toBeInTheDocument();
  });

  it("reports the chosen class id via onChange", async () => {
    listMock.mockResolvedValue([{ id: "c1", name: "כיתה א" }]);
    const onChange = vi.fn();

    renderWithClient(<ClassPicker id="class" value="" onChange={onChange} />);
    await screen.findByRole("option", { name: "כיתה א" });

    await userEvent.selectOptions(screen.getByRole("combobox"), "c1");

    expect(onChange).toHaveBeenCalledWith("c1");
  });

  it("hints to create a class when none exist", async () => {
    listMock.mockResolvedValue([]);

    renderWithClient(<ClassPicker id="class" value="" onChange={() => {}} />);

    await waitFor(() => expect(screen.getByText(/יש ליצור כיתה/)).toBeInTheDocument());
  });
});
