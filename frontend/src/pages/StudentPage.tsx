import { useCallback, useState, type ReactNode } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ChevronRight } from "lucide-react";
import { studentsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { LoadingState } from "@/components/ui/Spinner";
import { ErrorState } from "@/components/ui/ErrorState";
import { ProgramTab } from "@/pages/student/ProgramTab";
import { MeetingsTab } from "@/pages/student/MeetingsTab";
import { SocialNoteTab } from "@/pages/student/SocialNoteTab";
import { DetailsTab } from "@/pages/student/DetailsTab";
import { FunctionalReportTab } from "@/pages/student/FunctionalReportTab";
import { StudentActionsMenu } from "@/pages/student/StudentActionsMenu";

export function StudentPage(): ReactNode {
  const { studentId = "" } = useParams();
  const [searchParams] = useSearchParams();
  const requestedTab = searchParams.get("tab");
  const [autoOpenNew, setAutoOpenNew] = useState(() => searchParams.get("new") === "1");
  const consumeAutoOpen = useCallback(() => setAutoOpenNew(false), []);
  const { user } = useAuth();
  const query = useQuery({
    queryKey: queryKeys.student(studentId),
    queryFn: () => studentsApi.get(studentId),
    enabled: studentId !== "",
  });

  if (query.isLoading) {
    return <LoadingState />;
  }
  if (query.isError) {
    return <ErrorState error={query.error} />;
  }
  if (!query.data || !user) {
    return null;
  }

  const student = query.data;
  const showSocialNote = permissions.canReadSocialNote(user);
  const allowedTabs = showSocialNote
    ? ["details", "program", "meetings", "social-note", "functional-report"]
    : ["details", "program", "meetings", "functional-report"];
  const initialTab =
    requestedTab && allowedTabs.includes(requestedTab) ? requestedTab : "details";

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link
            to="/students"
            className="mb-2 inline-flex items-center gap-1 text-sm text-ink-muted hover:text-ink"
          >
            <ChevronRight className="h-4 w-4" />
            חזרה לרשימת התלמידים
          </Link>
          <h1 className="text-2xl font-bold text-ink">{student.full_name}</h1>
        </div>
        {permissions.canManage(user) && !student.is_archived && (
          <StudentActionsMenu student={student} />
        )}
      </div>

      <Tabs defaultValue={initialTab}>
        <TabsList>
          <TabsTrigger value="details">פרטים אישיים</TabsTrigger>
          <TabsTrigger value="program">תוכנית קידום</TabsTrigger>
          <TabsTrigger value="meetings">ישיבות צוות</TabsTrigger>
          {showSocialNote && <TabsTrigger value="social-note">סיכום עו״ס</TabsTrigger>}
          <TabsTrigger value="functional-report">סיכום דוח תפקודי</TabsTrigger>
        </TabsList>

        <TabsContent value="details">
          <DetailsTab studentId={student.id} />
        </TabsContent>
        <TabsContent value="program">
          <ProgramTab studentId={student.id} />
        </TabsContent>
        <TabsContent value="meetings">
          <MeetingsTab
            studentId={student.id}
            autoOpenNew={autoOpenNew}
            onAutoOpenConsumed={consumeAutoOpen}
          />
        </TabsContent>
        {showSocialNote && (
          <TabsContent value="social-note">
            <SocialNoteTab studentId={student.id} />
          </TabsContent>
        )}
        <TabsContent value="functional-report">
          <FunctionalReportTab studentId={student.id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
