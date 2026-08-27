import type { ReactNode } from "react";
import {
  useForm,
  useFieldArray,
  type Control,
  type UseFormRegister,
} from "react-hook-form";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { detailsApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  LegalStatus,
  StudentDetailsResponse,
  StudentDetailsUpsertRequest,
} from "@/lib/api/types";
import { legalStatusLabels } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

interface FormValues {
  national_id: string;
  date_of_birth: string;
  address: string;
  home_language: string;
  legal_status: LegalStatus | "";
  medical_diagnoses: { name: string; notes: string }[];
  emergency_contacts: { full_name: string; relationship: string; phone: string }[];
  guardians: { full_name: string; relationship: string; phone: string }[];
}

function toFormValues(details: StudentDetailsResponse): FormValues {
  return {
    national_id: details.national_id ?? "",
    date_of_birth: details.date_of_birth ?? "",
    address: details.address ?? "",
    home_language: details.home_language ?? "",
    legal_status: details.legal_status ?? "",
    medical_diagnoses: details.medical_diagnoses.map((diagnosis) => ({
      name: diagnosis.name,
      notes: diagnosis.notes ?? "",
    })),
    emergency_contacts: details.emergency_contacts.map((contact) => ({
      full_name: contact.full_name,
      relationship: contact.relationship ?? "",
      phone: contact.phone ?? "",
    })),
    guardians: details.guardians.map((contact) => ({
      full_name: contact.full_name,
      relationship: contact.relationship ?? "",
      phone: contact.phone ?? "",
    })),
  };
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

function toRequest(values: FormValues): StudentDetailsUpsertRequest {
  return {
    national_id: emptyToNull(values.national_id),
    date_of_birth: emptyToNull(values.date_of_birth),
    address: emptyToNull(values.address),
    home_language: emptyToNull(values.home_language),
    legal_status: values.legal_status === "" ? null : values.legal_status,
    medical_diagnoses: values.medical_diagnoses
      .filter((diagnosis) => diagnosis.name.trim() !== "")
      .map((diagnosis) => ({
        name: diagnosis.name.trim(),
        notes: emptyToNull(diagnosis.notes),
      })),
    emergency_contacts: values.emergency_contacts
      .filter((contact) => contact.full_name.trim() !== "")
      .map((contact) => ({
        full_name: contact.full_name.trim(),
        relationship: emptyToNull(contact.relationship),
        phone: emptyToNull(contact.phone),
      })),
    guardians: values.guardians
      .filter((contact) => contact.full_name.trim() !== "")
      .map((contact) => ({
        full_name: contact.full_name.trim(),
        relationship: emptyToNull(contact.relationship),
        phone: emptyToNull(contact.phone),
      })),
  };
}

interface Props {
  studentId: string;
  details: StudentDetailsResponse;
  onDone: () => void;
}

export function DetailsForm({ studentId, details, onDone }: Props): ReactNode {
  const queryClient = useQueryClient();
  const { register, control, handleSubmit } = useForm<FormValues>({
    defaultValues: toFormValues(details),
  });

  const mutation = useMutation({
    mutationFn: (values: FormValues) => detailsApi.upsert(studentId, toRequest(values)),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.details(studentId), data);
      void queryClient.invalidateQueries({ queryKey: queryKeys.program(studentId) });
      onDone();
    },
  });

  return (
    <form
      onSubmit={handleSubmit((values) => mutation.mutate(values))}
      className="space-y-6"
    >
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}

      <Card>
        <CardHeader>
          <CardTitle>זהות</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <div>
            <Label htmlFor="national_id">תעודת זהות</Label>
            <Input id="national_id" {...register("national_id")} maxLength={20} />
          </div>
          <div>
            <Label htmlFor="date_of_birth">תאריך לידה</Label>
            <Input id="date_of_birth" type="date" {...register("date_of_birth")} />
          </div>
          <div>
            <Label htmlFor="home_language">שפת בית</Label>
            <Input id="home_language" {...register("home_language")} maxLength={100} />
          </div>
          <div className="sm:col-span-2">
            <Label htmlFor="address">כתובת</Label>
            <Input id="address" {...register("address")} maxLength={300} />
          </div>
        </CardContent>
      </Card>

      <DiagnosisArray control={control} register={register} />

      <ContactArray
        title="אנשי קשר לחירום"
        name="emergency_contacts"
        control={control}
        register={register}
      />

      {details.sensitive_visible && (
        <Card>
          <CardHeader>
            <CardTitle>אפוטרופסות ומעמד משפטי</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="legal_status">מעמד משפטי</Label>
              <select
                id="legal_status"
                {...register("legal_status")}
                className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400"
              >
                <option value="">— לא צוין —</option>
                {(Object.keys(legalStatusLabels) as LegalStatus[]).map((status) => (
                  <option key={status} value={status}>
                    {legalStatusLabels[status]}
                  </option>
                ))}
              </select>
            </div>
            <ContactArray
              title="אפוטרופוסים"
              name="guardians"
              control={control}
              register={register}
              flat
            />
          </CardContent>
        </Card>
      )}

      <div className="flex justify-start gap-2">
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "שומר…" : "שמירה"}
        </Button>
        <Button type="button" variant="ghost" onClick={onDone}>
          ביטול
        </Button>
      </div>
    </form>
  );
}

function DiagnosisArray({
  control,
  register,
}: {
  control: Control<FormValues>;
  register: UseFormRegister<FormValues>;
}): ReactNode {
  const { fields, append, remove } = useFieldArray({
    control,
    name: "medical_diagnoses",
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>אבחנות רפואיות/תפקודיות</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {fields.map((field, index) => (
          <div key={field.id} className="flex items-start gap-2">
            <div className="grid flex-1 gap-2 sm:grid-cols-2">
              <Input
                placeholder="שם האבחנה"
                {...register(`medical_diagnoses.${index}.name`)}
              />
              <Input
                placeholder="הערות"
                {...register(`medical_diagnoses.${index}.notes`)}
              />
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => remove(index)}
            >
              <Trash2 className="h-4 w-4 text-rating-red" />
            </Button>
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append({ name: "", notes: "" })}
        >
          <Plus className="h-4 w-4" />
          הוספה
        </Button>
      </CardContent>
    </Card>
  );
}

type ContactArrayName = "emergency_contacts" | "guardians";

function ContactArray({
  title,
  name,
  control,
  register,
  flat = false,
}: {
  title: string;
  name: ContactArrayName;
  control: Control<FormValues>;
  register: UseFormRegister<FormValues>;
  flat?: boolean;
}): ReactNode {
  const { fields, append, remove } = useFieldArray({ control, name });

  const rows = (
    <div className="space-y-3">
      {fields.map((field, index) => (
        <div key={field.id} className="flex items-start gap-2">
          <div className="grid flex-1 gap-2 sm:grid-cols-3">
            <Input placeholder="שם מלא" {...register(`${name}.${index}.full_name`)} />
            <Input placeholder="קרבה" {...register(`${name}.${index}.relationship`)} />
            <Input placeholder="טלפון" {...register(`${name}.${index}.phone`)} />
          </div>
          <Button type="button" variant="ghost" size="icon" onClick={() => remove(index)}>
            <Trash2 className="h-4 w-4 text-rating-red" />
          </Button>
        </div>
      ))}
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => append({ full_name: "", relationship: "", phone: "" })}
      >
        <Plus className="h-4 w-4" />
        הוספה
      </Button>
    </div>
  );

  if (flat) {
    return (
      <div className="space-y-3">
        <div className="text-sm font-medium text-ink">{title}</div>
        {rows}
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>{rows}</CardContent>
    </Card>
  );
}
