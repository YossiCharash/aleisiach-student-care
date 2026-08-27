import { useState, type ReactNode } from "react";
import { authApi } from "@/lib/api/endpoints";
import { useAuth } from "@/lib/auth/AuthContext";
import { roleLabels } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";

export function PersonalSettingsPage(): ReactNode {
  const { user } = useAuth();
  const [sent, setSent] = useState(false);
  const [sending, setSending] = useState(false);

  if (!user) {
    return null;
  }

  async function requestReset(): Promise<void> {
    if (!user) {
      return;
    }
    setSending(true);
    try {
      await authApi.requestPasswordReset(user.email);
    } finally {
      setSending(false);
      setSent(true);
    }
  }

  return (
    <div className="max-w-xl">
      <h1 className="mb-6 text-2xl font-bold text-ink">הגדרות אישיות</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>הפרטים שלי</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-ink-muted">שם מלא</dt>
              <dd className="font-medium text-ink">{user.full_name}</dd>
            </div>
            <div>
              <dt className="text-ink-muted">דוא״ל</dt>
              <dd className="font-medium text-ink">{user.email}</dd>
            </div>
            <div>
              <dt className="text-ink-muted">שם משתמש</dt>
              <dd className="font-medium text-ink">{user.username ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-ink-muted">תפקיד</dt>
              <dd className="font-medium text-ink">{roleLabels[user.role]}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>שינוי סיסמה</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {sent ? (
            <Alert tone="success">
              נשלח קישור לאיפוס סיסמה לכתובת הדוא״ל שלך.
            </Alert>
          ) : (
            <>
              <p className="text-sm text-ink-muted">
                נשלח אליך קישור מאובטח לאיפוס הסיסמה בדוא״ל.
              </p>
              <Button onClick={requestReset} disabled={sending}>
                {sending ? "שולח…" : "שליחת קישור לשינוי סיסמה"}
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
