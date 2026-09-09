import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WorkshopPicker } from "@/components/WorkshopPicker";
import { renderWithClient } from "@/test/renderWithClient";
import { workshopsApi } from "@/lib/api/endpoints";

vi.mock("@/lib/api/endpoints", () => ({
  workshopsApi: { list: vi.fn() },
}));

const listMock = vi.mocked(workshopsApi.list);

describe("WorkshopPicker", () => {
  beforeEach(() => {
    listMock.mockReset();
  });

  it("loads classes from the server and renders them as options", async () => {
    listMock.mockResolvedValue([
      {
        id: "c1",
        name: "סדנה א",
        color: "#3F8420",
        instructor_id: null,
        instructor_name: null,
      },
      {
        id: "c2",
        name: "סדנה ב",
        color: "#85C441",
        instructor_id: null,
        instructor_name: null,
      },
    ]);

    renderWithClient(<WorkshopPicker id="class" value="" onChange={() => {}} />);

    expect(await screen.findByRole("option", { name: "סדנה א" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "סדנה ב" })).toBeInTheDocument();
  });

  it("reports the chosen class id via onChange", async () => {
    listMock.mockResolvedValue([
      {
        id: "c1",
        name: "סדנה א",
        color: "#3F8420",
        instructor_id: null,
        instructor_name: null,
      },
    ]);
    const onChange = vi.fn();

    renderWithClient(<WorkshopPicker id="class" value="" onChange={onChange} />);
    await screen.findByRole("option", { name: "סדנה א" });

    await userEvent.selectOptions(screen.getByRole("combobox"), "c1");

    expect(onChange).toHaveBeenCalledWith("c1");
  });

  it("hints to create a class when none exist", async () => {
    listMock.mockResolvedValue([]);

    renderWithClient(<WorkshopPicker id="class" value="" onChange={() => {}} />);

    await waitFor(() => expect(screen.getByText(/יש ליצור סדנה/)).toBeInTheDocument());
  });
});
