import { StrictMode, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { Button } from "@/components/ui/Button";
import { Eye } from "lucide-react";
import {
  AddSettingInput,
  EditableSettingRow,
  SettingsListCard,
} from "@/pages/settings/SettingsList";
import "@/index.css";

const noop = async (): Promise<void> => undefined;

function Group({
  heading,
  buttonLabel,
  items,
}: {
  heading: string;
  buttonLabel: string;
  items: string[];
}): ReactNode {
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-ink">{heading}</h3>
      <AddSettingInput placeholder="אפשרות חדשה" buttonLabel={buttonLabel} onSubmit={noop} />
      <SettingsListCard>
        {items.map((name) => (
          <EditableSettingRow key={name} name={name} onRename={noop} onSetActive={noop} />
        ))}
      </SettingsListCard>
    </div>
  );
}

function Preview(): ReactNode {
  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="mx-auto max-w-5xl space-y-6 rounded-card border border-slate-200 bg-white p-8 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-ink">עריכת פרטי תלמיד</h2>
            <p className="mt-1 text-sm text-ink-muted">
              ניהול האפשרויות של רשימות הבחירה בפרטי תלמיד. שינויים משתקפים מיד בטופס.
            </p>
          </div>
          <Button type="button" size="sm" variant="outline">
            <Eye className="h-4 w-4" />
            הצג מושבתות
          </Button>
        </div>

        <div className="grid grid-cols-2 items-start gap-x-6 gap-y-6">
          <Group
            heading="דרגת מגבלה שכלית התפתחותית"
            buttonLabel="הוספה"
            items={["קלה", "בינונית", "מורכבת"]}
          />
          <Group
            heading="מידת עצמאות בלקיחת תרופות"
            buttonLabel="הוספה"
            items={["אינו נוטל לבד", "זקוק לתזכורת והשגחה", "עצמאי"]}
          />
          <Group
            heading="אופן הבעה עיקרי"
            buttonLabel="הוספה"
            items={["מילולי", "תקשורת תומכת", "רמיזות", "שפת גוף"]}
          />
          <Group
            heading="כיתות"
            buttonLabel="הוספת כיתה"
            items={["כיתה א׳", "כיתה ב׳"]}
          />
        </div>
      </div>
    </div>
  );
}

createRoot(document.getElementById("preview-root") as HTMLElement).render(
  <StrictMode>
    <Preview />
  </StrictMode>
);
