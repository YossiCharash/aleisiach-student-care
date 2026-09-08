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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/Spinner";
import { EmptyState, ErrorState } from "@/components/ui/ErrorState";
import { RatingPill } from "@/components/RatingPill";
import { ProgramForm } from "@/pages/student/program/ProgramForm";
import { cn } from "@/lib/utils/cn";

export function ProgramTab({ studentId }: { studentId: string }): ReactNode {
  const { user } = useAuth();
  const [editing, setEditing] = useState(false);
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

  const program = query.data;

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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-ink-muted">
          {program.exists
            ? "מוקדי הכוח והמוקדים לחיזוק, והתוכנית האישית הנגזרת מהם."
            : "עדיין לא נבנתה תוכנית קידום לתלמיד."}
        </p>
        {canWrite && (
          <Button onClick={() => setEditing(true)}>
            {program.exists ? (
              <>
                <Pencil className="h-4 w-4" />
                עריכת תוכנית
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                יצירת תוכנית
              </>
            )}
          </Button>
        )}
      </div>

      {program.exists && <ProgramContent program={program} />}
    </div>
  );
}

function ProgramContent({ program }: { program: ProgramResponse }): ReactNode {
  const { strengths, areas_to_strengthen: areas } = program;
  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>מוקדי כוח</CardTitle>
          </CardHeader>
          <CardContent>
            {strengths.length === 0 ? (
              <EmptyState>אין עדיין מוקדי כוח.</EmptyState>
            ) : (
              <ul className="space-y-2">
                {strengths.map((strength) => (
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
            {areas.length === 0 ? (
              <EmptyState>אין עדיין מוקדים לחיזוק.</EmptyState>
            ) : (
              <ul className="space-y-3">
                {areas.map((area) => (
                  <AreaRow key={area.skill_id} area={area} />
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>תוכנית אישית</CardTitle>
        </CardHeader>
        <CardContent>
          <PersonalPlan areas={areas} />
        </CardContent>
      </Card>
    </div>
  );
}

const areaToneClass: Record<MeetingRating, string> = {
  green: "border-s-4 border-rating-green bg-accent-50/70",
  yellow: "border-s-4 border-rating-yellow bg-amber-50/80",
  red: "border-s-4 border-rating-red bg-red-50/80",
};

const areaTitleClass: Record<MeetingRating, string> = {
  green: "text-brand-700",
  yellow: "text-amber-800",
  red: "text-red-800",
};

function StrengthRow({ strength }: { strength: ProgramStrength }): ReactNode {
  return (
    <li className="rounded-lg border-s-4 border-rating-green bg-accent-50 px-3 py-2 font-medium text-brand-700">
      {strength.skill_name}
    </li>
  );
}

function AreaRow({ area }: { area: ProgramArea }): ReactNode {
  return (
    <li className={cn("rounded-lg px-3 py-2", areaToneClass[area.rating])}>
      <div className="flex items-center justify-between">
        <span className={cn("font-semibold", areaTitleClass[area.rating])}>
          {area.skill_name}
        </span>
        <RatingPill rating={area.rating} />
      </div>
      {area.solutions.length > 0 && (
        <div className="mt-2">
          <div className="mb-1 text-xs font-medium text-ink-muted">דרך לפתרון:</div>
          <ul className="list-disc space-y-0.5 pe-5 text-sm text-ink">
            {area.solutions.map((solution, index) => (
              <li key={index}>{solution}</li>
            ))}
          </ul>
        </div>
      )}
    </li>
  );
}

function PersonalPlan({ areas }: { areas: ProgramArea[] }): ReactNode {
  const withSolutions = areas.filter((area) => area.solutions.length > 0);
  if (withSolutions.length === 0) {
    return (
      <EmptyState>אין עדיין תוכנית אישית — הוסיפו דרכי פתרון למוקדים לחיזוק.</EmptyState>
    );
  }
  return (
    <ul className="space-y-3">
      {withSolutions.map((area) => (
        <li key={area.skill_id}>
          <div className="mb-1 font-medium text-ink">{area.skill_name}</div>
          <ul className="list-disc space-y-0.5 pe-5 text-sm text-ink-muted">
            {area.solutions.map((solution, index) => (
              <li key={index}>{solution}</li>
            ))}
          </ul>
        </li>
      ))}
    </ul>
  );
}
