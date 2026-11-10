import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HealthDomainsArea } from "@/pages/settings/HealthDomainsArea";
import { renderWithClient } from "@/test/renderWithClient";
import { healthDomainsApi } from "@/lib/api/endpoints";
import type { HealthDomainInfo } from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  healthDomainsApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
}));

const api = vi.mocked(healthDomainsApi);

const PHYSIO: HealthDomainInfo = {
  id: "d1",
  name: "פיזיותרפיה",
  order: 0,
  is_active: true,
};

describe("HealthDomainsArea", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("lists the institution's domains", async () => {
    api.list.mockResolvedValue([PHYSIO]);

    renderWithClient(<HealthDomainsArea />);

    expect(await screen.findByText("פיזיותרפיה")).toBeInTheDocument();
  });

  it("shows the empty state and adds a domain", async () => {
    api.list.mockResolvedValue([]);
    api.create.mockResolvedValue(PHYSIO);
    const user = userEvent.setup();

    renderWithClient(<HealthDomainsArea />);

    expect(await screen.findByText("עדיין לא הוגדרו תחומים.")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /הוספת תחום/ }));
    await user.type(screen.getByPlaceholderText("תחום חדש"), "ריפוי בעיסוק");
    await user.click(screen.getByRole("button", { name: "שמירה" }));

    expect(api.create).toHaveBeenCalledWith("ריפוי בעיסוק");
  });
});
