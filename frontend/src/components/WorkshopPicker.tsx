import type { ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { workshopsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import { Label } from "@/components/ui/Label";
import { errorMessage } from "@/components/ui/ErrorState";

interface Props {
  id: string;
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
}

export function WorkshopPicker({
  id,
  value,
  onChange,
  required = false,
}: Props): ReactNode {
  const query = useQuery({ queryKey: queryKeys.workshops, queryFn: workshopsApi.list });

  return (
    <div>
      <Label htmlFor={id}>סדנה</Label>
      <select
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        required={required}
        disabled={query.isLoading || query.isError}
        className="h-10 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm disabled:bg-slate-100"
      >
        <option value="" disabled>
          {query.isLoading ? "טוען סדנאות…" : "בחר/י סדנה"}
        </option>
        {query.data?.map((workshop) => (
          <option key={workshop.id} value={workshop.id}>
            {workshop.name}
          </option>
        ))}
      </select>
      {query.isError && (
        <p className="mt-1 text-xs text-rating-red">{errorMessage(query.error)}</p>
      )}
      {query.data?.length === 0 && (
        <p className="mt-1 text-xs text-ink-muted">
          אין סדנאות עדיין. יש ליצור סדנה בעמוד ההגדרות.
        </p>
      )}
    </div>
  );
}
