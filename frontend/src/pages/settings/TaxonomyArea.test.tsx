import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TaxonomyArea } from "@/pages/settings/TaxonomyArea";
import { renderWithClient } from "@/test/renderWithClient";
import { taxonomyApi } from "@/lib/api/endpoints";
import type { LabelTreeNode } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  taxonomyApi: {
    tree: vi.fn(),
    listLabels: vi.fn(),
    listSkills: vi.fn(),
    listSolutions: vi.fn(),
    createLabel: vi.fn(),
    createSkill: vi.fn(),
    createSolution: vi.fn(),
    updateLabel: vi.fn(),
    updateSkill: vi.fn(),
    updateSolution: vi.fn(),
  },
}));

const api = vi.mocked(taxonomyApi);

const tree: LabelTreeNode[] = [
  {
    id: "l1",
    name: "תווית פעילה",
    skills: [],
  },
];

const treeWithSkill: LabelTreeNode[] = [
  {
    id: "l1",
    name: "תווית פעילה",
    skills: [
      {
        id: "sk1",
        name: "הקשבה",
        green_text: "עצמאי",
        yellow_text: "בהשגחה",
        red_text: "בתלות",
        solutions: [
          { id: "so-y", text: "פתרון צהוב", rating: "yellow" },
          { id: "so-r", text: "פתרון אדום", rating: "red" },
        ],
      },
    ],
  },
];

describe("TaxonomyArea — reactivation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.tree.mockResolvedValue(tree);
    api.listLabels.mockResolvedValue([]);
    api.listSkills.mockResolvedValue([]);
    api.listSolutions.mockResolvedValue([]);
  });

  it("reactivates a deactivated skill from within its label", async () => {
    api.listSkills.mockResolvedValue([
      {
        id: "sk9",
        label_id: "l1",
        name: "כישור מושבת",
        order: 0,
        is_active: false,
        green_text: "ג",
        yellow_text: "צ",
        red_text: "א",
      },
    ]);
    api.updateSkill.mockResolvedValue({
      id: "sk9",
      label_id: "l1",
      name: "כישור מושבת",
      order: 0,
      is_active: true,
      green_text: "ג",
      yellow_text: "צ",
      red_text: "א",
    });

    renderWithClient(<TaxonomyArea />);

    await userEvent.click(await screen.findByRole("button", { name: "הצג מושבתים" }));
    await userEvent.click(await screen.findByRole("button", { name: "הרחב" }));
    await userEvent.click(await screen.findByRole("button", { name: /כישורים מושבתים/ }));

    expect(await screen.findByText("כישור מושבת")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /הפעלה מחדש/ }));

    await waitFor(() =>
      expect(api.updateSkill).toHaveBeenCalledWith("sk9", { is_active: true })
    );
  });

  it("lazily fetches inactive labels only when the section is opened", async () => {
    renderWithClient(<TaxonomyArea />);
    await screen.findByText("תווית פעילה");

    expect(api.listLabels).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "הצג מושבתים" }));
    expect(api.listLabels).not.toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: "תוויות מושבתות" }));

    await waitFor(() => expect(api.listLabels).toHaveBeenCalledWith(true));
  });

  it("hides the disabled sections until 'show disabled' is toggled on", async () => {
    renderWithClient(<TaxonomyArea />);
    await screen.findByText("תווית פעילה");

    expect(
      screen.queryByRole("button", { name: "תוויות מושבתות" })
    ).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "הצג מושבתים" }));

    expect(screen.getByRole("button", { name: "תוויות מושבתות" })).toBeInTheDocument();
  });
});

describe("TaxonomyArea — rating-scoped skills", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.tree.mockResolvedValue(tree);
    api.listLabels.mockResolvedValue([]);
    api.listSkills.mockResolvedValue([]);
    api.listSolutions.mockResolvedValue([]);
    api.createSkill.mockResolvedValue({
      id: "sk-new",
      label_id: "l1",
      name: "כישור חדש",
      order: 0,
      is_active: true,
      green_text: "ג",
      yellow_text: "צ",
      red_text: "א",
    });
  });

  it("creates a skill only after all three rating texts are filled", async () => {
    renderWithClient(<TaxonomyArea />);
    await userEvent.click(await screen.findByRole("button", { name: "הרחב" }));
    await userEvent.click(await screen.findByRole("button", { name: "הוספת כישור" }));

    await userEvent.type(screen.getByPlaceholderText("שם כישור"), "כישור חדש");

    const save = screen.getByRole("button", { name: "שמירת כישור" });
    expect(save).toBeDisabled();

    await userEvent.type(screen.getByLabelText("תיאור דרגת ירוק"), "ג");
    await userEvent.type(screen.getByLabelText("תיאור דרגת צהוב"), "צ");
    await userEvent.type(screen.getByLabelText("תיאור דרגת אדום"), "א");

    expect(save).toBeEnabled();
    await userEvent.click(save);

    await waitFor(() =>
      expect(api.createSkill).toHaveBeenCalledWith("l1", "כישור חדש", {
        green: "ג",
        yellow: "צ",
        red: "א",
      })
    );
  });

  it("adds a solution under the chosen rating and groups solutions by rating", async () => {
    api.tree.mockResolvedValue(treeWithSkill);
    api.createSolution.mockResolvedValue({
      id: "so-new",
      skill_id: "sk1",
      text: "פתרון חדש",
      rating: "yellow",
      is_active: true,
    });

    renderWithClient(<TaxonomyArea />);
    await userEvent.click(await screen.findByRole("button", { name: "הרחב" }));
    await userEvent.click(await screen.findByRole("button", { name: "הרחב" }));

    expect(await screen.findByText("פתרונות לדרגת בהשגחה")).toBeInTheDocument();
    expect(screen.getByText("פתרונות לדרגת בתלות")).toBeInTheDocument();
    expect(screen.getByText("פתרון צהוב")).toBeInTheDocument();
    expect(screen.getByText("פתרון אדום")).toBeInTheDocument();

    const addButtons = screen.getAllByRole("button", { name: "הוספת פתרון" });
    await userEvent.click(addButtons[0]);
    await userEvent.type(screen.getByPlaceholderText("טקסט פתרון"), "פתרון חדש");
    await userEvent.click(screen.getByRole("button", { name: "שמירה" }));

    await waitFor(() =>
      expect(api.createSolution).toHaveBeenCalledWith("sk1", "פתרון חדש", "yellow")
    );
  });
});
