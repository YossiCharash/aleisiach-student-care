import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { RiskDomainsArea } from "@/pages/settings/RiskDomainsArea";
import { renderWithClient } from "@/test/renderWithClient";
import { riskDomainsApi } from "@/lib/api/endpoints";
import type { RiskDomainInfo } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  riskDomainsApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
}));

const api = vi.mocked(riskDomainsApi);

const DOMAINS: RiskDomainInfo[] = [
  {
    id: "d1",
    category: "medical",
    category_label: "רפואי",
    name: "עודף / חוסר משקל",
    order: 0,
    is_active: true,
  },
  {
    id: "d2",
    category: "independence",
    category_label: "עצמאות",
    name: "ניידות בקהילה",
    order: 0,
    is_active: true,
  },
];

describe("RiskDomainsArea", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.list.mockResolvedValue(DOMAINS);
    api.create.mockResolvedValue(DOMAINS[0]);
  });

  it("groups the domains under their three categories", async () => {
    renderWithClient(<RiskDomainsArea />);

    const medical = (await screen.findByRole("heading", { name: "רפואי" })).closest(
      "section"
    );
    const behavioral = screen
      .getByRole("heading", { name: "התנהגותי" })
      .closest("section");
    expect(medical).not.toBeNull();
    expect(behavioral).not.toBeNull();
    expect(
      within(medical as HTMLElement).getByText("עודף / חוסר משקל")
    ).toBeInTheDocument();
    expect(
      within(behavioral as HTMLElement).getByText("אין תחומי סיכון בקטגוריה זו.")
    ).toBeInTheDocument();
  });

  it("adds a new domain to the chosen category", async () => {
    renderWithClient(<RiskDomainsArea />);

    const behavioral = (await screen.findByRole("heading", { name: "התנהגותי" })).closest(
      "section"
    ) as HTMLElement;
    await userEvent.click(within(behavioral).getByText("הוספת תחום"));
    await userEvent.type(
      within(behavioral).getByPlaceholderText("תחום סיכון חדש — התנהגותי"),
      "שימוש בטלפון{Enter}"
    );

    expect(api.create).toHaveBeenCalledWith("שימוש בטלפון", "behavioral");
  });
});
