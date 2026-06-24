import React from "react";
import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-surface-light dark:bg-surface-dark text-center px-6">
      <p className="font-display text-6xl font-semibold text-brand mb-2">404</p>
      <h1 className="font-display text-xl font-semibold mb-2">Page not found</h1>
      <p className="text-sm text-ink-400 dark:text-ink-100 mb-6">The page you're looking for doesn't exist or was moved.</p>
      <Link to="/dashboard" className="btn-primary">Back to dashboard</Link>
    </div>
  );
}
