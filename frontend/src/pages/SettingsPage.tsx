import type { ReactNode } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { UsersArea } from "@/pages/settings/UsersArea";
import { TaxonomyArea } from "@/pages/settings/TaxonomyArea";

export function SettingsPage(): ReactNode {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-ink">הגדרות</h1>
      <Tabs defaultValue="users">
        <TabsList>
          <TabsTrigger value="users">משתמשים</TabsTrigger>
          <TabsTrigger value="taxonomy">טקסונומיה</TabsTrigger>
        </TabsList>
        <TabsContent value="users">
          <UsersArea />
        </TabsContent>
        <TabsContent value="taxonomy">
          <TaxonomyArea />
        </TabsContent>
      </Tabs>
    </div>
  );
}
