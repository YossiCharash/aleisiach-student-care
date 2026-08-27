import { useState, type FormEvent, type ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/lib/auth/AuthContext";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Alert } from "@/components/ui/Alert";
import { errorMessage } from "@/components/ui/ErrorState";

export function LoginPage(): ReactNode {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent): Promise<void> {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      navigate("/", { replace: true });
    } catch (caught) {
      setError(errorMessage(caught, "שם המשתמש או הסיסמה שגויים."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AuthLayout title="כניסה למערכת" subtitle="הזינו שם משתמש וסיסמה">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert tone="error">{error}</Alert>}
        <div>
          <Label htmlFor="username">שם משתמש</Label>
          <Input
            id="username"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
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
            autoComplete="current-password"
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={submitting}>
          {submitting ? "מתחבר…" : "כניסה"}
        </Button>
        <div className="text-center text-sm">
          <Link to="/forgot-password" className="text-brand hover:underline">
            שכחתי סיסמה
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
