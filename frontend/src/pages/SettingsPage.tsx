import type { ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { UsersArea } from "@/pages/settings/UsersArea";
import { ClassesArea } from "@/pages/settings/ClassesArea";
import { TaxonomyArea } from "@/pages/settings/TaxonomyArea";
import { DiagnosesArea } from "@/pages/settings/DiagnosesArea";
import { DetailOptionsArea } from "@/pages/settings/DetailOptionsArea";
import { AccountArea } from "@/pages/settings/AccountArea";

const allTabs = [
  "users",
  "classes",
  "taxonomy",
  "diagnoses",
  "detail-options",
  "account",
] as const;
type SettingsTab = (typeof allTabs)[number];

export function SettingsPage(): ReactNode {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const canManage = user ? permissions.canManage(user) : false;
  const availableTabs: readonly SettingsTab[] = canManage ? allTabs : ["account"];
  const defaultTab: SettingsTab = canManage ? "users" : "account";

  const tabParam = searchParams.get("tab");
  const activeTab: SettingsTab =
    tabParam !== null && (availableTabs as readonly string[]).includes(tabParam)
      ? (tabParam as SettingsTab)
      : defaultTab;

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
          {canManage && (
            <>
              <TabsTrigger value="users">משתמשים</TabsTrigger>
              <TabsTrigger value="classes">כיתות</TabsTrigger>
              <TabsTrigger value="taxonomy">כישורים</TabsTrigger>
              <TabsTrigger value="diagnoses">אבחונים</TabsTrigger>
              <TabsTrigger value="detail-options">עריכת פרטי תלמיד</TabsTrigger>
            </>
          )}
          <TabsTrigger value="account">החשבון שלי</TabsTrigger>
        </TabsList>
        {canManage && (
          <>
            <TabsContent value="users">
              <UsersArea />
            </TabsContent>
            <TabsContent value="classes">
              <ClassesArea />
            </TabsContent>
            <TabsContent value="taxonomy">
              <TaxonomyArea />
            </TabsContent>
            <TabsContent value="diagnoses">
              <DiagnosesArea />
            </TabsContent>
            <TabsContent value="detail-options">
              <DetailOptionsArea />
            </TabsContent>
          </>
        )}
        <TabsContent value="account">
          <AccountArea />
        </TabsContent>
      </Tabs>
    </div>
  );
}
