import { useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { Pencil, Plus } from "lucide-react";
import { programApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  MeetingRating,
  ProgramArea,
  ProgramResponse,
  ProgramStrength,
} from "@/lib/api/types";
import { useAuth } from "@/lib/auth/AuthContext";
import { permissions } from "@/lib/auth/permissions";
import { cn } from "@/lib/utils/cn";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";
import { ProgramForm } from "@/pages/student/program/ProgramForm";
import { PersonalPlanTab } from "@/pages/student/program/PersonalPlanTab";

export function ProgramTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const canWrite = user ? permissions.canWriteProgram(user) : false;

  const query = useQuery({
    queryKey: queryKeys.program(studentId),
    queryFn: () => programApi.get(studentId),
  });

  if (query.isLoading) {
    return <LoadingState />;
  }
  if (query.isError) {
    return <ErrorState error={query.error} />;
  }
  if (!query.data) {
    return null;
  }

  return (
    <Tabs defaultValue="focus">
      <TabsList>
        <TabsTrigger value="focus">מוקדי כוח ומוקדים לחיזוק</TabsTrigger>
        <TabsTrigger value="personal">תוכנית אישית</TabsTrigger>
      </TabsList>

      <TabsContent value="focus">
        <FocusPanel studentId={studentId} program={query.data} canWrite={canWrite} />
      </TabsContent>

      <TabsContent value="personal">
        <PersonalPlanTab studentId={studentId} canWrite={canWrite} />
      </TabsContent>
    </Tabs>
  );
}

function FocusPanel({
  studentId,
  program,
  canWrite,
}: {
  studentId: string;
  program: ProgramResponse;
  canWrite: boolean;
}): ReactNode {
  const [editing, setEditing] = useState(false);

  if (editing) {
    return (
      <ProgramForm
        studentId={studentId}
        program={program}
        onDone={() => setEditing(false)}
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-muted">
          {program.exists
            ? "מוקדי הכוח והמוקדים לחיזוק של החניך."
            : "עדיין לא סומנו מוקדים לחניך."}
        </p>
        {canWrite && (
          <Button onClick={() => setEditing(true)}>
            {program.exists ? (
              <>
                <Pencil className="h-4 w-4" />
                עריכת מוקדים
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                יצירת מוקדים
              </>
            )}
          </Button>
        )}
      </div>

      {program.exists && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>מוקדי כוח</CardTitle>
            </CardHeader>
            <CardContent>
              {program.strengths.length === 0 ? (
                <EmptyState>אין מוקדי כוח.</EmptyState>
              ) : (
                <ul className="space-y-2">
                  {program.strengths.map((strength) => (
                    <StrengthRow key={strength.skill_id} strength={strength} />
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>מוקדים לחיזוק</CardTitle>
            </CardHeader>
            <CardContent>
              {program.areas_to_strengthen.length === 0 ? (
                <EmptyState>אין מוקדים לחיזוק.</EmptyState>
              ) : (
                <ul className="space-y-2">
                  {program.areas_to_strengthen.map((area) => (
                    <AreaRow key={area.skill_id} area={area} />
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

function StrengthRow({ strength }: { strength: ProgramStrength }): ReactNode {
  return (
    <li className="rounded-xl border-s-4 border-rating-green bg-accent-50 px-3.5 py-2.5 font-medium text-brand-700">
      {strength.skill_name}
    </li>
  );
}

const areaRowClass: Record<MeetingRating, string> = {
  green: "border-s-4 border-rating-green bg-accent-50 text-brand-700",
  yellow: "border-s-4 border-rating-yellow bg-amber-50 text-amber-800",
  red: "border-s-4 border-rating-red bg-red-50 text-red-800",
};

function AreaRow({ area }: { area: ProgramArea }): ReactNode {
  return (
    <li
      className={cn(
        "flex items-center justify-between gap-3 rounded-xl px-3.5 py-2.5 font-medium",
        areaRowClass[area.rating]
      )}
    >
      <span>{area.skill_name}</span>
      <RatingPill rating={area.rating} />
    </li>
  );
}
