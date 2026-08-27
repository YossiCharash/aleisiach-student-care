import { useState, type FormEvent, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { authApi } from "@/lib/api/endpoints";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";

const NEUTRAL_MESSAGE =
  "אם קיימת כתובת דוא\"ל תואמת במערכת, נשלח אליה קישור לאיפוס סיסמה.";

export function ForgotPasswordPage(): ReactNode {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent): Promise<void> {
    event.preventDefault();
    setSubmitting(true);
    try {
      await authApi.requestPasswordReset(email);
    } catch {
      // Neutral response regardless of outcome — no email enumeration leak.
    } finally {
      setSubmitting(false);
      setSubmitted(true);
    }
  }

  return (
    <AuthLayout title="שחזור סיסמה" subtitle="הזינו את כתובת הדוא״ל שלכם">
      {submitted ? (
        <div className="space-y-4">
          <Alert tone="success">{NEUTRAL_MESSAGE}</Alert>
          <Link to="/login" className="block text-center text-sm text-brand hover:underline">
            חזרה לכניסה
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">דוא״ל</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
              autoFocus
            />
          </div>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? "שולח…" : "שליחת קישור לאיפוס"}
          </Button>
          <Link to="/login" className="block text-center text-sm text-brand hover:underline">
            חזרה לכניסה
          </Link>
        </form>
      )}
    </AuthLayout>
  );
}
