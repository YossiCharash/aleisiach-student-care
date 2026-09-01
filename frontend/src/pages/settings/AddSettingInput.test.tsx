import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AddSettingInput } from "@/pages/settings/SettingsList";

describe("AddSettingInput", () => {
  it("shows only a button until it is clicked", () => {
    render(
      <AddSettingInput placeholder="אפשרות חדשה" buttonLabel="הוספה" onSubmit={vi.fn()} />
    );

    expect(screen.getByRole("button", { name: "הוספה" })).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
  });

  it("reveals the input on click and submits the trimmed value with Enter", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <AddSettingInput
        placeholder="אפשרות חדשה"
        buttonLabel="הוספה"
        onSubmit={onSubmit}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: "הוספה" }));
    const input = screen.getByPlaceholderText("אפשרות חדשה");
    await userEvent.type(input, "  קלה  ");
    await userEvent.keyboard("{Enter}");

    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith("קלה"));
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "הוספה" })).toBeInTheDocument();
  });

  it("submits via the save button", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <AddSettingInput
        placeholder="אפשרות חדשה"
        buttonLabel="הוספה"
        onSubmit={onSubmit}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: "הוספה" }));
    await userEvent.type(screen.getByPlaceholderText("אפשרות חדשה"), "בינונית");
    await userEvent.click(screen.getByRole("button", { name: "שמירה" }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith("בינונית"));
  });

  it("collapses without submitting when cancelled", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <AddSettingInput
        placeholder="אפשרות חדשה"
        buttonLabel="הוספה"
        onSubmit={onSubmit}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: "הוספה" }));
    await userEvent.type(screen.getByPlaceholderText("אפשרות חדשה"), "משהו");
    await userEvent.click(screen.getByRole("button", { name: "ביטול" }));

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "הוספה" })).toBeInTheDocument();
  });

  it("does not submit an empty value", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <AddSettingInput
        placeholder="אפשרות חדשה"
        buttonLabel="הוספה"
        onSubmit={onSubmit}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: "הוספה" }));
    await userEvent.keyboard("{Enter}");

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "שמירה" })).toBeDisabled();
  });
});
