import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "../components/common/Primitives";

export default function Login() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    const result = await login(identifier, password);
    setSubmitting(false);
    if (result.success) {
      navigate(location.state?.from || "/dashboard", { replace: true });
    } else {
      setError(result.message);
    }
  };

  return (
    <AuthLayout title="Welcome back" subtitle="Log in to pick up where you left off.">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg bg-critical-100 text-critical-500 text-sm px-3 py-2">{error}</div>
        )}
        <div>
          <label className="label" htmlFor="identifier">Username or email</label>
          <input
            id="identifier"
            className="input"
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder="admin or admin@taskmanager.local"
            required
            autoFocus
          />
        </div>
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="label mb-0" htmlFor="password">Password</label>
            <Link to="/forgot-password" className="text-xs text-brand hover:underline">Forgot password?</Link>
          </div>
          <input
            id="password"
            type="password"
            className="input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={submitting}>
          {submitting && <Spinner className="h-4 w-4" />}
          Log in
        </button>
      </form>

      <p className="text-sm text-ink-400 dark:text-ink-100 mt-6 text-center">
        New here?{" "}
        <Link to="/register" className="text-brand font-medium hover:underline">
          Create an account
        </Link>
      </p>

      <div className="mt-8 pt-6 border-t border-black/[0.06] dark:border-white/[0.06] text-xs text-ink-400 space-y-1">
        <p className="font-medium">Demo accounts (after running the seed script):</p>
        <p>admin / Admin@12345</p>
        <p>pmorgan / Manager@12345</p>
        <p>jchen / Member@12345</p>
      </div>
    </AuthLayout>
  );
}
