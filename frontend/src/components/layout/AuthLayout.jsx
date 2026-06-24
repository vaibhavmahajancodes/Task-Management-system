import React from "react";

export function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="min-h-screen flex bg-surface-light dark:bg-surface-dark">
      <div className="hidden lg:flex lg:w-1/2 bg-ink relative overflow-hidden flex-col justify-between p-12 text-white">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-md bg-brand flex items-center justify-center">
            <div className="h-3 w-3 rounded-sm bg-amber" />
          </div>
          <span className="font-display font-semibold text-lg">Task Manager</span>
        </div>

        <div className="max-w-md">
          <h1 className="font-display text-4xl font-semibold leading-tight mb-4">
            Plan the work.
            <br />
            Track the progress.
            <br />
            Ship it together.
          </h1>
          <p className="text-ink-100 text-sm leading-relaxed">
            Kanban boards, deadlines, time tracking, and team insights in one place built for teams who'd
            rather be building than status-checking.
          </p>
        </div>

        <div className="flex gap-6 text-xs text-ink-100">
          <div>
            <p className="font-display text-2xl font-semibold text-white">16+</p>
            <p>Feature areas</p>
          </div>
          <div>
            <p className="font-display text-2xl font-semibold text-white">Real-time</p>
            <p>Live board sync</p>
          </div>
          <div>
            <p className="font-display text-2xl font-semibold text-white">RBAC</p>
            <p>Role-based access</p>
          </div>
        </div>

        <div className="absolute -right-20 -bottom-20 h-72 w-72 rounded-full bg-brand/20 blur-3xl" aria-hidden="true" />
      </div>

      <div className="flex-1 flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-2 mb-8 justify-center">
            <div className="h-7 w-7 rounded-md bg-brand flex items-center justify-center">
              <div className="h-2.5 w-2.5 rounded-sm bg-amber" />
            </div>
            <span className="font-display font-semibold">Task Manager</span>
          </div>
          <h2 className="font-display text-2xl font-semibold mb-1">{title}</h2>
          {subtitle && <p className="text-sm text-ink-400 dark:text-ink-100 mb-6">{subtitle}</p>}
          {children}
        </div>
      </div>
    </div>
  );
}
