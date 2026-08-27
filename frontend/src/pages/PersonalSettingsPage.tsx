import { useState, type FormEvent, type ReactNode } from "react";
import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/lib/api/endpoints";
import { useAuth } from "@/lib/auth/AuthContext";
import { roleLabels } from "@/lib/utils/hebrew";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

const MIN_PASSWORD_LENGTH = 8;

export function PersonalSettingsPage(): ReactNode {
  const { user } = useAuth();

  if (!user) {
    return null;
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
        <CardContent>
          <ChangePasswordForm />
        </CardContent>
      </Card>
    </div>
  );
}

function ChangePasswordForm(): ReactNode {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const mutation = useMutation({
    mutationFn: () =>
      authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    onSuccess: () => {
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setDone(true);
    },
  });

  function handleSubmit(event: FormEvent): void {
    event.preventDefault();
    setDone(false);
    if (newPassword.length < MIN_PASSWORD_LENGTH) {
      setValidationError(`הסיסמה החדשה חייבת להכיל לפחות ${MIN_PASSWORD_LENGTH} תווים.`);
      return;
    }
    if (newPassword !== confirmPassword) {
      setValidationError("הסיסמאות אינן תואמות.");
      return;
    }
    setValidationError(null);
    mutation.mutate();
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {done && <Alert tone="success">הסיסמה שונתה בהצלחה.</Alert>}
      {validationError && <Alert tone="error">{validationError}</Alert>}
      {mutation.isError && <Alert tone="error">{errorMessage(mutation.error)}</Alert>}
      <div>
        <Label htmlFor="current-password">סיסמה נוכחית</Label>
        <Input
          id="current-password"
          type="password"
          autoComplete="current-password"
          value={currentPassword}
          onChange={(event) => setCurrentPassword(event.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="new-password">סיסמה חדשה</Label>
        <Input
          id="new-password"
          type="password"
          autoComplete="new-password"
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
          required
        />
      </div>
      <div>
        <Label htmlFor="confirm-password">אימות סיסמה חדשה</Label>
        <Input
          id="confirm-password"
          type="password"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          required
        />
      </div>
      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? "שומר…" : "שינוי סיסמה"}
      </Button>
    </form>
  );
}
