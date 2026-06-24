import React from "react";
import { NavLink } from "react-router-dom";
import clsx from "clsx";
import {
  FiGrid,
  FiFolder,
  FiCheckSquare,
  FiTrello,
  FiCalendar,
  FiBarChart2,
  FiUsers,
  FiSettings,
} from "react-icons/fi";
import { useAuth } from "../../context/AuthContext";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: FiGrid },
  { to: "/projects", label: "Projects", icon: FiFolder },
  { to: "/tasks", label: "Tasks", icon: FiCheckSquare },
  { to: "/calendar", label: "Calendar", icon: FiCalendar },
  { to: "/reports", label: "Reports", icon: FiBarChart2 },
  { to: "/team", label: "Team", icon: FiUsers },
];

export function Sidebar({ open, onClose }) {
  const { user } = useAuth();

  return (
    <>
      {open && <div className="fixed inset-0 bg-black/30 z-30 md:hidden" onClick={onClose} aria-hidden="true" />}
      <aside
        className={clsx(
          "fixed md:static inset-y-0 left-0 z-40 w-60 shrink-0 bg-ink text-white flex flex-col transition-transform duration-200",
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
      >
        <div className="flex items-center gap-2 px-5 h-16 shrink-0">
          <div className="h-7 w-7 rounded-md bg-brand flex items-center justify-center">
            <div className="h-2.5 w-2.5 rounded-sm bg-amber" />
          </div>
          <span className="font-display font-semibold tracking-tight">Task Manager</span>
        </div>

        <nav className="flex-1 px-3 py-2 space-y-0.5 overflow-y-auto">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive ? "bg-brand text-white" : "text-ink-100 hover:bg-white/5 hover:text-white"
                )
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}

          {user?.role === "admin" && (
            <NavLink
              to="/audit-log"
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive ? "bg-brand text-white" : "text-ink-100 hover:bg-white/5 hover:text-white"
                )
              }
            >
              <FiSettings size={17} />
              Audit Log
            </NavLink>
          )}
        </nav>

        <div className="px-3 py-4 border-t border-white/10">
          <NavLink
            to="/settings"
            onClick={onClose}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive ? "bg-brand text-white" : "text-ink-100 hover:bg-white/5 hover:text-white"
              )
            }
          >
            <FiSettings size={17} />
            Settings
          </NavLink>
        </div>
      </aside>
    </>
  );
}
