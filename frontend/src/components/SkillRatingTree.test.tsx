import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import { renderWithClient } from "@/test/renderWithClient";
import { SkillRatingTree } from "@/components/SkillRatingTree";
import { taxonomyApi } from "@/lib/api/endpoints";
import type { LabelTreeNode } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  taxonomyApi: { tree: vi.fn() },
}));

const treeMock = vi.mocked(taxonomyApi.tree);

const tree: LabelTreeNode[] = [
  {
    id: "l1",
    name: "עצמאות",
    sub_labels: [
      {
        id: "sl1",
        name: "היגיינה",
        skills: [{ id: "sk1", name: "רחיצת ידיים", solutions: [] }],
      },
    ],
  },
];

describe("SkillRatingTree", () => {
  beforeEach(() => {
    treeMock.mockReset();
  });

  it("renders the taxonomy skills", async () => {
    treeMock.mockResolvedValue(tree);

    renderWithClient(<SkillRatingTree drafts={{}} setDraft={vi.fn()} />);

    expect(await screen.findByText("עצמאות")).toBeInTheDocument();
    expect(screen.getByText("רחיצת ידיים")).toBeInTheDocument();
  });

  it("shows an empty message when no taxonomy is defined", async () => {
    treeMock.mockResolvedValue([]);

    renderWithClient(<SkillRatingTree drafts={{}} setDraft={vi.fn()} />);

    expect(
      await screen.findByText("לא הוגדרה טקסונומיה. יש להגדיר בהגדרות תחילה.")
    ).toBeInTheDocument();
  });
});
