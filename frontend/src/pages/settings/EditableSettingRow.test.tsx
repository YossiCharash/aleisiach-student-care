import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import { EditableSettingRow } from "@/pages/settings/SettingsList";

function renderRow(row: ReactElement): HTMLElement {
  const { container } = render(<ul>{row}</ul>);
  return container.querySelector("li") as HTMLElement;
}

describe("EditableSettingRow", () => {
  it("renames with the trimmed draft and leaves edit mode", async () => {
    const onRename = vi.fn().mockResolvedValue(undefined);
    renderRow(<EditableSettingRow name="קלה" onRename={onRename} />);

    await userEvent.click(screen.getByRole("button", { name: "עריכה" }));
    const input = screen.getByDisplayValue("קלה");
    await userEvent.clear(input);
    await userEvent.type(input, "  בינונית  ");
    await userEvent.keyboard("{Enter}");

    await waitFor(() => expect(onRename).toHaveBeenCalledWith("בינונית"));
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "עריכה" })).toBeInTheDocument();
  });

  it("does not call onRename when the value is unchanged", async () => {
    const onRename = vi.fn().mockResolvedValue(undefined);
    renderRow(<EditableSettingRow name="קלה" onRename={onRename} />);

    await userEvent.click(screen.getByRole("button", { name: "עריכה" }));
    await userEvent.keyboard("{Enter}");

    expect(onRename).not.toHaveBeenCalled();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("restores the original name and stays put when editing is cancelled", async () => {
    const onRename = vi.fn().mockResolvedValue(undefined);
    renderRow(<EditableSettingRow name="קלה" onRename={onRename} />);

    await userEvent.click(screen.getByRole("button", { name: "עריכה" }));
    await userEvent.type(screen.getByRole("textbox"), "משהו");
    await userEvent.keyboard("{Escape}");

    expect(onRename).not.toHaveBeenCalled();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.getByText("קלה")).toBeInTheDocument();
  });

  it("deactivates an active row", async () => {
    const onSetActive = vi.fn().mockResolvedValue(undefined);
    renderRow(
      <EditableSettingRow name="עצמאי" onRename={vi.fn()} onSetActive={onSetActive} />
    );

    await userEvent.click(screen.getByRole("button", { name: "השבתה" }));

    expect(onSetActive).toHaveBeenCalledWith(false);
  });

  it("shows only reactivation for an inactive row", async () => {
    const onSetActive = vi.fn().mockResolvedValue(undefined);
    renderRow(
      <EditableSettingRow
        name="ישן"
        isActive={false}
        onRename={vi.fn()}
        onSetActive={onSetActive}
      />
    );

    expect(screen.queryByRole("button", { name: "עריכה" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "השבתה" })).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "הפעלה מחדש" }));

    expect(onSetActive).toHaveBeenCalledWith(true);
  });

  it("omits activation controls when onSetActive is not provided", () => {
    const row = renderRow(<EditableSettingRow name="כיתה א" onRename={vi.fn()} />);

    expect(within(row).getByRole("button", { name: "עריכה" })).toBeInTheDocument();
    expect(within(row).queryByRole("button", { name: "השבתה" })).not.toBeInTheDocument();
    expect(
      within(row).queryByRole("button", { name: "הפעלה מחדש" })
    ).not.toBeInTheDocument();
  });

  it("surfaces the server message when deactivation is refused", async () => {
    const onSetActive = vi
      .fn()
      .mockRejectedValue(new Error("לא ניתן להעביר את הכיתה לארכיון."));
    renderRow(
      <EditableSettingRow name="כיתה א" onRename={vi.fn()} onSetActive={onSetActive} />
    );

    await userEvent.click(screen.getByRole("button", { name: "השבתה" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "לא ניתן להעביר את הכיתה לארכיון."
    );
  });

  it("clears a previous action error on the next attempt", async () => {
    const onSetActive = vi
      .fn()
      .mockRejectedValueOnce(new Error("נכשל"))
      .mockResolvedValueOnce(undefined);
    renderRow(
      <EditableSettingRow name="כיתה א" onRename={vi.fn()} onSetActive={onSetActive} />
    );

    await userEvent.click(screen.getByRole("button", { name: "השבתה" }));
    expect(await screen.findByRole("alert")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "השבתה" }));

    await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
  });
});
