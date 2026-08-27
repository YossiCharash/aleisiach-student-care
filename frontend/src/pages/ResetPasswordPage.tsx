import { useState, type FormEvent, type ReactNode } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { authApi } from "@/lib/api/endpoints";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

export function ResetPasswordPage(): ReactNode {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent): Promise<void> {
    event.preventDefault();
    setError(null);
    if (password !== confirm) {
      setError("הסיסמאות אינן תואמות.");
      return;
    }
    setSubmitting(true);
    try {
      await authApi.confirmPasswordReset(token, password);
      navigate("/login", { replace: true, state: { passwordReset: true } });
    } catch (caught) {
      setError(errorMessage(caught, "קישור האיפוס אינו תקף או שפג תוקפו."));
    } finally {
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <AuthLayout title="איפוס סיסמה">
        <Alert tone="error">קישור האיפוס חסר או שגוי.</Alert>
        <Link
          to="/login"
          className="mt-4 block text-center text-sm text-brand hover:underline"
        >
          חזרה לכניסה
        </Link>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="איפוס סיסמה" subtitle="בחרו סיסמה חדשה">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert tone="error">{error}</Alert>}
        <div>
          <Label htmlFor="password">סיסמה חדשה</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            maxLength={128}
            autoComplete="new-password"
            required
            autoFocus
          />
          <p className="mt-1 text-xs text-ink-muted">לפחות 8 תווים.</p>
        </div>
        <div>
          <Label htmlFor="confirm">אישור סיסמה</Label>
          <Input
            id="confirm"
            type="password"
            value={confirm}
            onChange={(event) => setConfirm(event.target.value)}
            autoComplete="new-password"
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={submitting}>
          {submitting ? "מאפס…" : "איפוס סיסמה"}
        </Button>
      </form>
    </AuthLayout>
  );
}
