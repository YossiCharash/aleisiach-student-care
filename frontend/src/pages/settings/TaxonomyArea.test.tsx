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
    listSubLabels: vi.fn(),
    listSkills: vi.fn(),
    listSolutions: vi.fn(),
    createLabel: vi.fn(),
    createSubLabel: vi.fn(),
    createSkill: vi.fn(),
    createSolution: vi.fn(),
    updateLabel: vi.fn(),
    updateSubLabel: vi.fn(),
    updateSkill: vi.fn(),
    updateSolution: vi.fn(),
  },
}));

const api = vi.mocked(taxonomyApi);

const tree: LabelTreeNode[] = [
  {
    id: "l1",
    name: "תווית פעילה",
    sub_labels: [{ id: "sl1", name: "תת-תווית פעילה", skills: [] }],
  },
];

describe("TaxonomyArea — reactivation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.tree.mockResolvedValue(tree);
    api.listLabels.mockResolvedValue([]);
    api.listSubLabels.mockResolvedValue([]);
    api.listSkills.mockResolvedValue([]);
    api.listSolutions.mockResolvedValue([]);
  });

  it("reactivates a deactivated sub-label from within its label", async () => {
    api.listSubLabels.mockResolvedValue([
      { id: "sl9", label_id: "l1", name: "תת-תווית מושבתת", order: 0, is_active: false },
    ]);
    api.updateSubLabel.mockResolvedValue({
      id: "sl9",
      label_id: "l1",
      name: "תת-תווית מושבתת",
      order: 0,
      is_active: true,
    });

    renderWithClient(<TaxonomyArea />);

    await userEvent.click(await screen.findByRole("button", { name: "הצג מושבתים" }));
    await userEvent.click(await screen.findByRole("button", { name: "הרחב" }));
    await userEvent.click(
      await screen.findByRole("button", { name: /תת-תוויות מושבתות/ })
    );

    expect(await screen.findByText("תת-תווית מושבתת")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /הפעלה מחדש/ }));

    await waitFor(() =>
      expect(api.updateSubLabel).toHaveBeenCalledWith("sl9", { is_active: true })
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

    expect(
      screen.getByRole("button", { name: "תוויות מושבתות" })
    ).toBeInTheDocument();
  });
});
