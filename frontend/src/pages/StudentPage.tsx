import type { ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
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
import { StudentActionsMenu } from "@/pages/student/StudentActionsMenu";

export function StudentPage(): ReactNode {
  const { studentId = "" } = useParams();
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

      <Tabs defaultValue="program">
        <TabsList>
          <TabsTrigger value="program">תוכנית</TabsTrigger>
          <TabsTrigger value="meetings">ישיבות צוות</TabsTrigger>
          {showSocialNote && <TabsTrigger value="social-note">הערת עו״ס</TabsTrigger>}
          <TabsTrigger value="details">פרטי תלמיד</TabsTrigger>
        </TabsList>

        <TabsContent value="program">
          <ProgramTab studentId={student.id} />
        </TabsContent>
        <TabsContent value="meetings">
          <MeetingsTab studentId={student.id} />
        </TabsContent>
        {showSocialNote && (
          <TabsContent value="social-note">
            <SocialNoteTab studentId={student.id} />
          </TabsContent>
        )}
        <TabsContent value="details">
          <DetailsTab studentId={student.id} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
