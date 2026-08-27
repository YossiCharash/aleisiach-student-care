import { useState, type FormEvent, type ReactNode } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { authApi } from "@/lib/api/endpoints";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

export function AcceptInvitationPage(): ReactNode {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
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
      await authApi.acceptInvitation({ token, username, password });
      navigate("/login", { replace: true, state: { invited: true } });
    } catch (caught) {
      setError(errorMessage(caught, "קישור ההזמנה אינו תקף או שפג תוקפו."));
    } finally {
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <AuthLayout title="הזמנה למערכת">
        <Alert tone="error">קישור ההזמנה חסר או שגוי.</Alert>
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
    <AuthLayout title="הפעלת חשבון" subtitle="בחרו שם משתמש וסיסמה">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert tone="error">{error}</Alert>}
        <div>
          <Label htmlFor="username">שם משתמש</Label>
          <Input
            id="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            minLength={3}
            maxLength={80}
            autoComplete="username"
            required
            autoFocus
          />
        </div>
        <div>
          <Label htmlFor="password">סיסמה</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            minLength={8}
            maxLength={128}
            autoComplete="new-password"
            required
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
          {submitting ? "מפעיל…" : "הפעלת חשבון"}
        </Button>
      </form>
    </AuthLayout>
  );
}
