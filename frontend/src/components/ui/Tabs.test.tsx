import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";

function renderTabs(variant?: "underline" | "pill") {
  return render(
    <Tabs defaultValue="a">
      <TabsList variant={variant}>
        <TabsTrigger value="a">ראשון</TabsTrigger>
        <TabsTrigger value="b">שני</TabsTrigger>
      </TabsList>
      <TabsContent value="a">תוכן ראשון</TabsContent>
    </Tabs>
  );
}

describe("Tabs", () => {
  it("renders the active tab content", () => {
    renderTabs();
    expect(screen.getByText("תוכן ראשון")).toBeInTheDocument();
  });

  it("styles triggers as underline tabs by default", () => {
    renderTabs();
    expect(screen.getByRole("tab", { name: "ראשון" }).className).toContain("border-b-2");
  });

  it("styles triggers as pills when the list asks for them", () => {
    renderTabs("pill");
    const trigger = screen.getByRole("tab", { name: "ראשון" });
    expect(trigger.className).toContain("data-[state=active]:bg-white");
    expect(trigger.className).not.toContain("border-b-2");
  });
});
