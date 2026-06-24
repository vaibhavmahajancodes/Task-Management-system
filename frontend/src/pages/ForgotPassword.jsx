import React, { useState } from "react";
import { Link } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { authService } from "../services/authService";
import { apiErrorMessage } from "../services/api";
import { Spinner } from "../components/common/Primitives";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await authService.forgotPassword(email);
      setSent(true);
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthLayout title="Reset your password" subtitle="We'll email you a link to choose a new one.">
      {sent ? (
        <div className="rounded-lg bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300 text-sm px-4 py-3">
          If that email is registered, a reset link is on its way. Check your inbox.
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <div className="rounded-lg bg-critical-100 text-critical-500 text-sm px-3 py-2">{error}</div>}
          <div>
            <label className="label" htmlFor="email">Email</label>
            <input id="email" type="email" className="input" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus />
          </div>
          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting && <Spinner className="h-4 w-4" />}
            Send reset link
          </button>
        </form>
      )}
      <p className="text-sm text-ink-400 dark:text-ink-100 mt-6 text-center">
        <Link to="/login" className="text-brand font-medium hover:underline">Back to log in</Link>
      </p>
    </AuthLayout>
  );
}
