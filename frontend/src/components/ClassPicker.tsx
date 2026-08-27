import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { classesApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { Label } from "@/components/ui/Label";
import { errorMessage } from "@/components/ui/ErrorState";

interface Props {
  id: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
}

export function ClassPicker({ id, value, onChange, required = false }: Props): ReactNode {
  const query = useQuery({ queryKey: queryKeys.classes, queryFn: classesApi.list });

  return (
    <div>
      <Label htmlFor={id}>כיתה</Label>
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        required={required}
        disabled={query.isLoading || query.isError}
        className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm disabled:bg-slate-100"
      >
        <option value="" disabled>
          {query.isLoading ? "טוען כיתות…" : "בחר/י כיתה"}
        </option>
        {query.data?.map((classItem) => (
          <option key={classItem.id} value={classItem.id}>
            {classItem.name}
          </option>
        ))}
      </select>
      {query.isError && (
        <p className="mt-1 text-xs text-rating-red">{errorMessage(query.error)}</p>
      )}
      {query.data?.length === 0 && (
        <p className="mt-1 text-xs text-ink-muted">
          אין כיתות עדיין. יש ליצור כיתה בעמוד ההגדרות.
        </p>
      )}
    </div>
  );
}
