import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { userService } from "../services/domainServices";
import { useToast } from "../context/ToastContext";
import { apiErrorMessage } from "../services/api";
import { Avatar, Spinner } from "../components/common/Primitives";
import { FiSun, FiMoon } from "react-icons/fi";

export default function Settings() {
  const { user, updateLocalUser } = useAuth();
  const { theme, setTheme } = useTheme();
  const { showToast } = useToast();

  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || "",
    job_title: user?.job_title || "",
    avatar_url: user?.avatar_url || "",
  });
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
  });
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  const handleProfileSave = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      const updated = await userService.updateProfile(profileForm);
      updateLocalUser(updated);
      showToast("Profile updated.", "success");
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSave = async (e) => {
    e.preventDefault();
    setSavingPassword(true);
    try {
      await userService.changePassword(passwordForm);
      showToast("Password changed successfully.", "success");
      setPasswordForm({ current_password: "", new_password: "" });
    } catch (error) {
      showToast(apiErrorMessage(error, "Could not update password."), "error");
    } finally {
      setSavingPassword(false);
    }
  };

  const handleThemeChoice = async (value) => {
    setTheme(value);
    try {
      const updated = await userService.updateProfile({ theme_preference: value });
      updateLocalUser(updated);
    } catch {
      /* best-effort server sync */
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="font-display text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-ink-400 dark:text-ink-100">
          Manage your profile, security, and appearance.
        </p>
      </div>

      {/* Profile */}
      <div className="card p-5">
        <h2 className="font-display font-semibold mb-4">Profile</h2>
        <form onSubmit={handleProfileSave} className="space-y-4">
          <div className="flex items-center gap-3">
            <Avatar user={user} size="lg" />
            <div className="flex-1">
              <label className="label">Avatar URL</label>
              <input
                className="input"
                placeholder="https://..."
                value={profileForm.avatar_url}
                onChange={(e) => setProfileForm((f) => ({ ...f, avatar_url: e.target.value }))}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Full name</label>
              <input
                className="input"
                value={profileForm.full_name}
                onChange={(e) => setProfileForm((f) => ({ ...f, full_name: e.target.value }))}
              />
            </div>
            <div>
              <label className="label">Job title</label>
              <input
                className="input"
                value={profileForm.job_title}
                onChange={(e) => setProfileForm((f) => ({ ...f, job_title: e.target.value }))}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm text-ink-400">
            <p>Username: <span className="text-ink dark:text-surface-light">{user?.username}</span></p>
            <p>Email: <span className="text-ink dark:text-surface-light">{user?.email}</span></p>
          </div>
          <button type="submit" className="btn-primary" disabled={savingProfile}>
            {savingProfile && <Spinner className="h-4 w-4" />}
            Save profile
          </button>
        </form>
      </div>

      {/* Appearance */}
      <div className="card p-5">
        <h2 className="font-display font-semibold mb-4">Appearance</h2>
        <div className="flex gap-3">
          <button
            onClick={() => handleThemeChoice("light")}
            className={"flex-1 flex items-center justify-center gap-2 rounded-lg border-2 py-3 text-sm " +
              (theme === "light"
                ? "border-brand text-brand"
                : "border-ink-100 dark:border-white/10 text-ink-400")}
          >
            <FiSun size={16} /> Light
          </button>
          <button
            onClick={() => handleThemeChoice("dark")}
            className={"flex-1 flex items-center justify-center gap-2 rounded-lg border-2 py-3 text-sm " +
              (theme === "dark"
                ? "border-brand text-brand"
                : "border-ink-100 dark:border-white/10 text-ink-400")}
          >
            <FiMoon size={16} /> Dark
          </button>
        </div>
      </div>

      {/* Change Password */}
      <div className="card p-5">
        <h2 className="font-display font-semibold mb-4">Change password</h2>
        <form onSubmit={handlePasswordSave} className="space-y-4">
          <div>
            <label className="label">Current password</label>
            <input
              type="password"
              className="input"
              required
              value={passwordForm.current_password}
              onChange={(e) => setPasswordForm((f) => ({ ...f, current_password: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">New password (min 8 characters)</label>
            <input
              type="password"
              className="input"
              required
              minLength={8}
              value={passwordForm.new_password}
              onChange={(e) => setPasswordForm((f) => ({ ...f, new_password: e.target.value }))}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={savingPassword}>
            {savingPassword && <Spinner className="h-4 w-4" />}
            Update password
          </button>
        </form>
      </div>
    </div>
  );
}
