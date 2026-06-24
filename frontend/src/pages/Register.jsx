import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AuthLayout } from "../components/layout/AuthLayout";
import { useAuth } from "../context/AuthContext";
import { Spinner } from "../components/common/Primitives";

export default function Register() {
  const [form, setForm] = useState({ username: "", email: "", full_name: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (form.password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setSubmitting(true);
    const result = await register(form);
    setSubmitting(false);
    if (result.success) navigate("/dashboard", { replace: true });
    else setError(result.message);
  };

  return (
    <AuthLayout title="Create your account" subtitle="Start organizing projects in minutes.">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <div className="rounded-lg bg-critical-100 text-critical-500 text-sm px-3 py-2">{error}</div>}
        <div>
          <label className="label" htmlFor="full_name">Full name</label>
          <input id="full_name" className="input" value={form.full_name} onChange={update("full_name")} placeholder="Ava Administrator" />
        </div>
        <div>
          <label className="label" htmlFor="username">Username</label>
          <input id="username" className="input" value={form.username} onChange={update("username")} placeholder="ava" required minLength={3} />
        </div>
        <div>
          <label className="label" htmlFor="email">Email</label>
          <input id="email" type="email" className="input" value={form.email} onChange={update("email")} placeholder="ava@company.com" required />
        </div>
        <div>
          <label className="label" htmlFor="password">Password</label>
          <input id="password" type="password" className="input" value={form.password} onChange={update("password")} placeholder="At least 8 characters" required minLength={8} />
        </div>
        <button type="submit" className="btn-primary w-full" disabled={submitting}>
          {submitting && <Spinner className="h-4 w-4" />}
          Create account
        </button>
      </form>

      <p className="text-sm text-ink-400 dark:text-ink-100 mt-6 text-center">
        Already have an account?{" "}
        <Link to="/login" className="text-brand font-medium hover:underline">
          Log in
        </Link>
      </p>
    </AuthLayout>
  );
}
