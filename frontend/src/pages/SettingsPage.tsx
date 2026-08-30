import type { ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { UsersArea } from "@/pages/settings/UsersArea";
import { ClassesArea } from "@/pages/settings/ClassesArea";
import { TaxonomyArea } from "@/pages/settings/TaxonomyArea";

const tabs = ["users", "classes", "taxonomy"] as const;
type SettingsTab = (typeof tabs)[number];

function isSettingsTab(value: string | null): value is SettingsTab {
  return value !== null && (tabs as readonly string[]).includes(value);
}

export function SettingsPage(): ReactNode {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab");
  const activeTab: SettingsTab = isSettingsTab(tabParam) ? tabParam : "users";

  function handleTabChange(value: string): void {
    setSearchParams(
      (previous) => {
        const next = new URLSearchParams(previous);
        next.set("tab", value);
        return next;
      },
      { replace: true }
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-ink">הגדרות</h1>
      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <TabsList>
          <TabsTrigger value="users">משתמשים</TabsTrigger>
          <TabsTrigger value="classes">כיתות</TabsTrigger>
          <TabsTrigger value="taxonomy">טקסונומיה</TabsTrigger>
        </TabsList>
        <TabsContent value="users">
          <UsersArea />
        </TabsContent>
        <TabsContent value="classes">
          <ClassesArea />
        </TabsContent>
        <TabsContent value="taxonomy">
          <TaxonomyArea />
        </TabsContent>
      </Tabs>
    </div>
  );
}
