import type { ReactNode } from "react";
import {
  useForm,
  useFieldArray,
  useWatch,
  type Control,
  type UseFormRegister,
} from "react-hook-form";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { detailOptionsApi, detailsApi, diagnosesApi } from "@/lib/api/endpoints";
import { queryKeys } from "@/lib/api/queryKeys";
import type {
  DetailOptionField,
  LegalStatus,
  StudentDetailsResponse,
  StudentDetailsUpsertRequest,
} from "@/lib/api/types";
import { IDD_DIAGNOSIS_NAME, legalStatusLabels } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

interface TextItem {
  value: string;
}

interface ContactItem {
  full_name: string;
  relationship: string;
  phone: string;
}

interface FormValues {
  national_id: string;
  date_of_birth: string;
  address: string;
  home_language: string;
  idd_severity: string;
  additional_diagnoses: TextItem[];
  emergency_contacts: ContactItem[];
  legal_status: LegalStatus | "";
  guardians: ContactItem[];
  has_allergies_or_dietary: boolean;
  allergies_dietary: TextItem[];
  takes_regular_medication: boolean;
  medications: TextItem[];
  medication_independence: string;
  emergency_protocol: string;
  assistive_devices: string[];
  assistive_device_other: string;
  expression_mode: string;
  language_comprehension: string;
  current_or_last_framework: string;
  prior_task_experience: string;
  interests_strengths: string;
  triggers: string;
  distress_early_signs: string;
  calming_methods: string;
}

type OptionsFor = (field: DetailOptionField) => string[];

const selectClass =
  "h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400";

function mergeMissing(options: string[], extra: string[]): string[] {
  const merged = [...options];
  for (const value of extra) {
    if (value !== "" && !merged.includes(value)) {
      merged.push(value);
    }
  }
  return merged;
}

function toContactItems(contacts: StudentDetailsResponse["guardians"]): ContactItem[] {
  return contacts.map((contact) => ({
    full_name: contact.full_name,
    relationship: contact.relationship ?? "",
    phone: contact.phone ?? "",
  }));
}

function toFormValues(details: StudentDetailsResponse): FormValues {
  return {
    national_id: details.national_id ?? "",
    date_of_birth: details.date_of_birth ?? "",
    address: details.address ?? "",
    home_language: details.home_language ?? "",
    idd_severity: details.idd_severity ?? "",
    additional_diagnoses: details.additional_diagnoses.map((value) => ({ value })),
    emergency_contacts: toContactItems(details.emergency_contacts),
    legal_status: details.legal_status ?? "",
    guardians: toContactItems(details.guardians),
    has_allergies_or_dietary: details.has_allergies_or_dietary,
    allergies_dietary: details.allergies_dietary.map((value) => ({ value })),
    takes_regular_medication: details.takes_regular_medication,
    medications: details.medications.map((value) => ({ value })),
    medication_independence: details.medication_independence ?? "",
    emergency_protocol: details.emergency_protocol ?? "",
    assistive_devices: details.assistive_devices,
    assistive_device_other: details.assistive_device_other ?? "",
    expression_mode: details.expression_mode ?? "",
    language_comprehension: details.language_comprehension ?? "",
    current_or_last_framework: details.current_or_last_framework ?? "",
    prior_task_experience: details.prior_task_experience ?? "",
    interests_strengths: details.interests_strengths ?? "",
    triggers: details.triggers ?? "",
    distress_early_signs: details.distress_early_signs ?? "",
    calming_methods: details.calming_methods ?? "",
  };
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed === "" ? null : trimmed;
}

function items(list: TextItem[]): string[] {
  return list.map((item) => item.value.trim()).filter((value) => value !== "");
}

function toContacts(list: ContactItem[]): StudentDetailsResponse["guardians"] {
  return list
    .filter((contact) => contact.full_name.trim() !== "")
    .map((contact) => ({
      full_name: contact.full_name.trim(),
      relationship: emptyToNull(contact.relationship),
      phone: emptyToNull(contact.phone),
    }));
}

function toRequest(values: FormValues): StudentDetailsUpsertRequest {
  return {
    national_id: emptyToNull(values.national_id),
    date_of_birth: emptyToNull(values.date_of_birth),
    address: emptyToNull(values.address),
    home_language: emptyToNull(values.home_language),
    idd_severity: emptyToNull(values.idd_severity),
    additional_diagnoses: items(values.additional_diagnoses),
    emergency_contacts: toContacts(values.emergency_contacts),
    legal_status: values.legal_status === "" ? null : values.legal_status,
    guardians: toContacts(values.guardians),
    has_allergies_or_dietary: values.has_allergies_or_dietary,
    allergies_dietary: items(values.allergies_dietary),
    takes_regular_medication: values.takes_regular_medication,
    medications: items(values.medications),
    medication_independence: emptyToNull(values.medication_independence),
    emergency_protocol: emptyToNull(values.emergency_protocol),
    assistive_devices: values.assistive_devices,
    assistive_device_other: emptyToNull(values.assistive_device_other),
    expression_mode: emptyToNull(values.expression_mode),
    language_comprehension: emptyToNull(values.language_comprehension),
    current_or_last_framework: emptyToNull(values.current_or_last_framework),
    prior_task_experience: emptyToNull(values.prior_task_experience),
    interests_strengths: emptyToNull(values.interests_strengths),
    triggers: emptyToNull(values.triggers),
    distress_early_signs: emptyToNull(values.distress_early_signs),
    calming_methods: emptyToNull(values.calming_methods),
  };
}

interface Props {
  studentId: string;
  details: StudentDetailsResponse;
  onDone: () => void;
}

export function DetailsForm({ studentId, details, onDone }: Props): ReactNode {
  const queryClient = useQueryClient();
  const { register, control, handleSubmit, formState } = useForm<FormValues>({
    defaultValues: toFormValues(details),
  });
  const optionsQuery = useQuery({
    queryKey: queryKeys.detailOptions,
    queryFn: () => detailOptionsApi.list(),
  });

  const optionsFor: OptionsFor = (field) =>
    (optionsQuery.data ?? [])
      .filter((option) => option.field === field)
      .map((option) => option.name);

  const mutation = useMutation({
    mutationFn: (values: FormValues) => detailsApi.upsert(studentId, toRequest(values)),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.details(studentId), data);
      void queryClient.invalidateQueries({ queryKey: queryKeys.program(studentId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.diagnoses });
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
            <Label htmlFor="home_language">שפת דיבור עיקרית בבית</Label>
            <Input id="home_language" {...register("home_language")} maxLength={100} />
          </div>
          <div className="sm:col-span-2">
            <Label htmlFor="address">כתובת</Label>
            <Input id="address" {...register("address")} maxLength={300} />
          </div>
        </CardContent>
      </Card>

      <DiagnosesCard
        control={control}
        register={register}
        severityOptions={mergeMissing(optionsFor("idd_severity"), [
          details.idd_severity ?? "",
        ])}
        error={!!formState.errors.idd_severity}
      />

      <ContactArray
        title="אנשי קשר לחירום"
        name="emergency_contacts"
        control={control}
        register={register}
      />

      <MedicalProfileCard
        control={control}
        register={register}
        details={details}
        optionsFor={optionsFor}
      />

      <CommunicationCard register={register} details={details} optionsFor={optionsFor} />

      <BackgroundCard register={register} />

      <EmotionalIdCard register={register} />

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
                className={selectClass}
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

function OptionSelect({
  id,
  register,
  name,
  options,
  required,
}: {
  id: string;
  register: UseFormRegister<FormValues>;
  name:
    | "idd_severity"
    | "medication_independence"
    | "expression_mode"
    | "language_comprehension";
  options: string[];
  required?: boolean;
}): ReactNode {
  return (
    <select id={id} {...register(name, { required })} className={selectClass}>
      <option value="">{required ? "— בחר/י —" : "— לא צוין —"}</option>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
}

function DiagnosesCard({
  control,
  register,
  severityOptions,
  error,
}: {
  control: Control<FormValues>;
  register: UseFormRegister<FormValues>;
  severityOptions: string[];
  error: boolean;
}): ReactNode {
  const catalog = useQuery({
    queryKey: queryKeys.diagnoses,
    queryFn: () => diagnosesApi.list(),
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>אבחונים</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="idd_severity">{IDD_DIAGNOSIS_NAME} — דרגה</Label>
          <OptionSelect
            id="idd_severity"
            register={register}
            name="idd_severity"
            options={severityOptions}
            required
          />
          {error && (
            <p className="mt-1 text-sm text-rating-red">יש לבחור דרגה לפני שמירה.</p>
          )}
        </div>

        <datalist id="diagnosis-options">
          {(catalog.data ?? []).map((entry) => (
            <option key={entry.id} value={entry.name} />
          ))}
        </datalist>
        <StringArray
          control={control}
          register={register}
          name="additional_diagnoses"
          label="אבחנות נוספות"
          placeholder="בחר/י מהרשימה או הקלד/י אבחנה חדשה"
          datalistId="diagnosis-options"
        />
      </CardContent>
    </Card>
  );
}

function MedicalProfileCard({
  control,
  register,
  details,
  optionsFor,
}: {
  control: Control<FormValues>;
  register: UseFormRegister<FormValues>;
  details: StudentDetailsResponse;
  optionsFor: OptionsFor;
}): ReactNode {
  const hasAllergies = useWatch({ control, name: "has_allergies_or_dietary" });
  const takesMedication = useWatch({ control, name: "takes_regular_medication" });
  const deviceOptions = mergeMissing(
    optionsFor("assistive_device"),
    details.assistive_devices
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>פרופיל רפואי ובטיחותי קריטי</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <label className="flex items-center gap-2 text-sm font-medium text-ink">
          <input type="checkbox" {...register("has_allergies_or_dietary")} />
          יש אלרגיות / מגבלות תזונה
        </label>
        {hasAllergies && (
          <StringArray
            control={control}
            register={register}
            name="allergies_dietary"
            label="פירוט אלרגיות / מגבלות"
            placeholder="תיאור"
          />
        )}

        <label className="flex items-center gap-2 text-sm font-medium text-ink">
          <input type="checkbox" {...register("takes_regular_medication")} />
          נוטל/ת תרופות קבועות
        </label>
        {takesMedication && (
          <div className="space-y-4">
            <StringArray
              control={control}
              register={register}
              name="medications"
              label="תרופות"
              placeholder="שם התרופה"
            />
            <div>
              <Label htmlFor="medication_independence">מידת עצמאות בלקיחת תרופות</Label>
              <OptionSelect
                id="medication_independence"
                register={register}
                name="medication_independence"
                options={mergeMissing(optionsFor("medication_independence"), [
                  details.medication_independence ?? "",
                ])}
              />
            </div>
          </div>
        )}

        <div>
          <Label htmlFor="emergency_protocol">פרוטוקול חירום רפואי</Label>
          <Textarea
            id="emergency_protocol"
            rows={3}
            maxLength={5000}
            {...register("emergency_protocol")}
          />
        </div>

        <div>
          <div className="mb-2 text-sm font-medium text-ink">אביזרי עזר פיזיים</div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {deviceOptions.map((device) => (
              <label key={device} className="flex items-center gap-2 text-sm text-ink">
                <input
                  type="checkbox"
                  value={device}
                  {...register("assistive_devices")}
                />
                {device}
              </label>
            ))}
          </div>
          <div className="mt-2">
            <Label htmlFor="assistive_device_other">אביזר עזר נוסף (פירוט)</Label>
            <Input
              id="assistive_device_other"
              maxLength={200}
              {...register("assistive_device_other")}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function CommunicationCard({
  register,
  details,
  optionsFor,
}: {
  register: UseFormRegister<FormValues>;
  details: StudentDetailsResponse;
  optionsFor: OptionsFor;
}): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>ערוץ תקשורת מועדף</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-2">
        <div>
          <Label htmlFor="expression_mode">אופן הבעה עיקרי</Label>
          <OptionSelect
            id="expression_mode"
            register={register}
            name="expression_mode"
            options={mergeMissing(optionsFor("expression_mode"), [
              details.expression_mode ?? "",
            ])}
          />
        </div>
        <div>
          <Label htmlFor="language_comprehension">מידת הבנת השפה</Label>
          <OptionSelect
            id="language_comprehension"
            register={register}
            name="language_comprehension"
            options={mergeMissing(optionsFor("language_comprehension"), [
              details.language_comprehension ?? "",
            ])}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function BackgroundCard({
  register,
}: {
  register: UseFormRegister<FormValues>;
}): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>רקע חינוכי ותעסוקתי קודם</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="current_or_last_framework">מסגרת נוכחית או אחרונה</Label>
          <Input
            id="current_or_last_framework"
            maxLength={300}
            {...register("current_or_last_framework")}
          />
        </div>
        <div>
          <Label htmlFor="prior_task_experience">ניסיון קודם במטלות / עבודות</Label>
          <Textarea
            id="prior_task_experience"
            rows={3}
            maxLength={2000}
            {...register("prior_task_experience")}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function EmotionalIdCard({
  register,
}: {
  register: UseFormRegister<FormValues>;
}): ReactNode {
  return (
    <Card>
      <CardHeader>
        <CardTitle>תעודת זהות רגשית</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="interests_strengths">תחומי עניין וחוזקות</Label>
          <Textarea
            id="interests_strengths"
            rows={2}
            maxLength={2000}
            {...register("interests_strengths")}
          />
        </div>
        <div>
          <Label htmlFor="triggers">גורמים מציפים / טריגרים</Label>
          <Textarea id="triggers" rows={2} maxLength={2000} {...register("triggers")} />
        </div>
        <div>
          <Label htmlFor="distress_early_signs">סימנים מקדימים למצוקה</Label>
          <Textarea
            id="distress_early_signs"
            rows={2}
            maxLength={2000}
            {...register("distress_early_signs")}
          />
        </div>
        <div>
          <Label htmlFor="calming_methods">דרכי הרגעה מומלצות</Label>
          <Textarea
            id="calming_methods"
            rows={2}
            maxLength={2000}
            {...register("calming_methods")}
          />
        </div>
      </CardContent>
    </Card>
  );
}

type StringArrayName = "additional_diagnoses" | "allergies_dietary" | "medications";

function StringArray({
  control,
  register,
  name,
  label,
  placeholder,
  datalistId,
}: {
  control: Control<FormValues>;
  register: UseFormRegister<FormValues>;
  name: StringArrayName;
  label: string;
  placeholder: string;
  datalistId?: string;
}): ReactNode {
  const { fields, append, remove } = useFieldArray({ control, name });

  return (
    <div className="space-y-2">
      <div className="text-sm font-medium text-ink">{label}</div>
      {fields.map((field, index) => (
        <div key={field.id} className="flex items-center gap-2">
          <Input
            className="flex-1"
            placeholder={placeholder}
            list={datalistId}
            {...register(`${name}.${index}.value`)}
          />
          <Button type="button" variant="ghost" size="icon" onClick={() => remove(index)}>
            <Trash2 className="h-4 w-4 text-rating-red" />
          </Button>
        </div>
      ))}
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => append({ value: "" })}
      >
        <Plus className="h-4 w-4" />
        הוספה
      </Button>
    </div>
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
