import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { authService } from "../services/authService";
import { apiErrorMessage } from "../services/api";
import { Spinner } from "../components/common/Primitives";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!token) {
      setError("This reset link is missing its token. Please request a new one.");
      return;
    }
    setSubmitting(true);
    try {
      await authService.resetPassword(token, password);
      navigate("/login", { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err, "This reset link is invalid or has expired."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Choose a new password" subtitle="Make it something you haven't used before.">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="rounded-lg bg-critical-100 text-critical-500 text-sm px-3 py-2">{error}</div>}
        <div>
          <label className="label" htmlFor="password">New password</label>
          <input
            id="password"
            type="password"
            className="input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            autoFocus
          />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={submitting}>
          {submitting && <Spinner className="h-4 w-4" />}
          Reset password
        </button>
      </form>
      <p className="text-sm text-ink-400 dark:text-ink-100 mt-6 text-center">
        <Link to="/login" className="text-brand font-medium hover:underline">Back to log in</Link>
      </p>
    </AuthLayout>
  );
}
