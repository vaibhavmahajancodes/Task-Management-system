import React from "react";
import clsx from "clsx";

const PRIORITY_STYLES = {
  low: "bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100",
  medium: "bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300",
  high: "bg-amber-100 text-amber-600",
  critical: "bg-critical-100 text-critical-500",
};

export function PriorityBadge({ priority }) {
  return (
    <span className={clsx("badge", PRIORITY_STYLES[priority] || PRIORITY_STYLES.medium)}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {priority?.charAt(0).toUpperCase() + priority?.slice(1)}
    </span>
  );
}

const STATUS_STYLES = {
  planning: "bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100",
  active: "bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300",
  on_hold: "bg-amber-100 text-amber-600",
  completed: "bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300",
  archived: "bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100",
  todo: "bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100",
  in_progress: "bg-amber-100 text-amber-600",
  review: "bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300",
};

export function StatusBadge({ status }) {
  const label = status?.replace(/_/g, " ");
  return (
    <span className={clsx("badge", STATUS_STYLES[status] || STATUS_STYLES.todo)}>
      {label?.charAt(0).toUpperCase() + label?.slice(1)}
    </span>
  );
}

export function Avatar({ user, size = "md" }) {
  const sizes = { sm: "h-6 w-6 text-[10px]", md: "h-8 w-8 text-xs", lg: "h-12 w-12 text-base" };
  const initials = (user?.full_name || user?.username || "?")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  if (user?.avatar_url) {
    return <img src={user.avatar_url} alt={user.username} className={clsx("rounded-full object-cover", sizes[size])} />;
  }

  return (
    <div
      title={user?.full_name || user?.username}
      className={clsx(
        "flex items-center justify-center rounded-full bg-brand text-white font-semibold shrink-0",
        sizes[size]
      )}
    >
      {initials}
    </div>
  );
}

export function Spinner({ className }) {
  return (
    <svg className={clsx("animate-spin", className)} viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-16 px-6">
      {icon && <div className="text-4xl mb-3 text-ink-100 dark:text-white/10">{icon}</div>}
      <h3 className="font-display font-semibold text-lg mb-1">{title}</h3>
      {description && <p className="text-sm text-ink-400 dark:text-ink-100 max-w-sm mb-4">{description}</p>}
      {action}
    </div>
  );
}

export function FullPageSpinner() {
  return (
    <div className="flex h-screen w-full items-center justify-center bg-surface-light dark:bg-surface-dark">
      <Spinner className="h-8 w-8 text-brand" />
    </div>
  );
}
