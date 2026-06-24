import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { FiMenu, FiBell, FiSun, FiMoon, FiSearch, FiLogOut, FiUser } from "react-icons/fi";
import { useAuth } from "../../context/AuthContext";
import { useTheme } from "../../context/ThemeContext";
import { useNotifications } from "../../context/NotificationContext";
import { Avatar } from "../common/Primitives";
import { formatDistanceToNow } from "date-fns";

export function Topbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { notifications, unreadCount, markRead, markAllRead } = useNotifications();
  const [notifOpen, setNotifOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [search, setSearch] = useState("");
  const navigate = useNavigate();
  const notifRef = useRef(null);
  const userRef = useRef(null);

  useEffect(() => {
    function onClickOutside(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false);
      if (userRef.current && !userRef.current.contains(e.target)) setUserMenuOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    if (search.trim()) navigate(`/tasks?search=${encodeURIComponent(search.trim())}`);
  };

  return (
    <header className="h-16 shrink-0 flex items-center gap-3 px-4 md:px-6 border-b border-black/[0.06] dark:border-white/[0.06] bg-surface-card dark:bg-surface-darkcard">
      <button
        className="md:hidden p-2 rounded-lg hover:bg-ink-50 dark:hover:bg-white/5"
        onClick={onMenuClick}
        aria-label="Open navigation menu"
      >
        <FiMenu size={20} />
      </button>

      <form onSubmit={handleSearch} className="hidden sm:flex flex-1 max-w-md relative">
        <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" size={16} />
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search tasks..."
          className="input pl-9"
          aria-label="Global search"
        />
      </form>

      <div className="flex-1 sm:hidden" />

      <div className="flex items-center gap-1.5">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg text-ink-400 hover:bg-ink-50 dark:hover:bg-white/5"
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? <FiSun size={18} /> : <FiMoon size={18} />}
        </button>

        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setNotifOpen((o) => !o)}
            className="relative p-2 rounded-lg text-ink-400 hover:bg-ink-50 dark:hover:bg-white/5"
            aria-label="Notifications"
          >
            <FiBell size={18} />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-critical" />
            )}
          </button>
          {notifOpen && (
            <div className="absolute right-0 mt-2 w-80 card shadow-popover animate-slide-up z-50 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-3 border-b border-black/[0.06] dark:border-white/[0.06]">
                <span className="font-medium text-sm">Notifications</span>
                {unreadCount > 0 && (
                  <button onClick={markAllRead} className="text-xs text-brand hover:underline">
                    Mark all read
                  </button>
                )}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.length === 0 ? (
                  <p className="text-sm text-ink-400 px-4 py-6 text-center">You're all caught up.</p>
                ) : (
                  notifications.map((n) => (
                    <button
                      key={n.id}
                      onClick={() => {
                        if (!n.is_read) markRead(n.id);
                        if (n.link) navigate(n.link);
                        setNotifOpen(false);
                      }}
                      className={`w-full text-left px-4 py-3 text-sm border-b border-black/[0.04] dark:border-white/[0.04] hover:bg-ink-50 dark:hover:bg-white/5 ${
                        !n.is_read ? "bg-brand-50/60 dark:bg-brand-900/20" : ""
                      }`}
                    >
                      <p>{n.message}</p>
                      <p className="text-xs text-ink-400 mt-1">
                        {formatDistanceToNow(new Date(n.created_at), { addSuffix: true })}
                      </p>
                    </button>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="relative" ref={userRef}>
          <button onClick={() => setUserMenuOpen((o) => !o)} className="flex items-center gap-2 p-1 rounded-lg hover:bg-ink-50 dark:hover:bg-white/5">
            <Avatar user={user} size="sm" />
          </button>
          {userMenuOpen && (
            <div className="absolute right-0 mt-2 w-48 card shadow-popover animate-slide-up z-50 py-1">
              <div className="px-3 py-2 border-b border-black/[0.06] dark:border-white/[0.06]">
                <p className="text-sm font-medium truncate">{user?.full_name || user?.username}</p>
                <p className="text-xs text-ink-400 truncate">{user?.email}</p>
              </div>
              <button
                onClick={() => {
                  setUserMenuOpen(false);
                  navigate("/settings");
                }}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-ink-50 dark:hover:bg-white/5"
              >
                <FiUser size={15} /> Profile
              </button>
              <button
                onClick={logout}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-critical hover:bg-critical-100/50"
              >
                <FiLogOut size={15} /> Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
