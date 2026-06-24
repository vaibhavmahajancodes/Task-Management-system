import React, { useEffect, useState } from "react";
import { FiUserCheck, FiUserX, FiUsers } from "react-icons/fi";
import { userService } from "../services/domainServices";
import { Spinner, Avatar, EmptyState } from "../components/common/Primitives";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiErrorMessage } from "../services/api";

const ROLES = ["admin", "project_manager", "team_member"];

export default function TeamManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [onlineIds, setOnlineIds] = useState([]);
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();
  const isAdmin = currentUser?.role === "admin";

  const load = () => {
    setLoading(true);
    Promise.all([userService.list(), userService.online()])
      .then(([list, online]) => {
        setUsers(list);
        setOnlineIds(online);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleRoleChange = async (userId, role) => {
    try {
      await userService.updateRole(userId, role);
      showToast("Role updated.", "success");
      load();
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  const handleToggleActive = async (member) => {
    try {
      if (member.is_active) await userService.deactivate(member.id);
      else await userService.activate(member.id);
      load();
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Team</h1>
        <p className="text-sm text-ink-400 dark:text-ink-100">Everyone with access to your workspace.</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-24">
          <Spinner className="h-7 w-7 text-brand" />
        </div>
      ) : users.length === 0 ? (
        <EmptyState icon={<FiUsers />} title="No team members yet" />
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-ink-50/60 dark:bg-white/5 text-left text-xs text-ink-400">
              <tr>
                <th className="px-4 py-3 font-medium">Member</th>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium hidden sm:table-cell">Status</th>
                {isAdmin && <th className="px-4 py-3 font-medium text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-black/[0.06] dark:divide-white/[0.06]">
              {users.map((member) => (
                <tr key={member.id}>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <Avatar user={member} size="sm" />
                        {onlineIds.includes(member.id) && (
                          <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-brand ring-2 ring-surface-card dark:ring-surface-darkcard" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{member.full_name || member.username}</p>
                        <p className="text-xs text-ink-400">@{member.username}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {isAdmin ? (
                      <select
                        className="input py-1 text-xs max-w-[160px]"
                        value={member.role}
                        onChange={(e) => handleRoleChange(member.id, e.target.value)}
                      >
                        {ROLES.map((r) => <option key={r} value={r}>{r.replace("_", " ")}</option>)}
                      </select>
                    ) : (
                      <span className="badge bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100 capitalize">
                        {member.role.replace("_", " ")}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 hidden sm:table-cell">
                    <span className={`badge ${member.is_active ? "bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300" : "bg-critical-100 text-critical-500"}`}>
                      {member.is_active ? "Active" : "Deactivated"}
                    </span>
                  </td>
                  {isAdmin && (
                    <td className="px-4 py-3 text-right">
                      {member.id !== currentUser.id && (
                        <button
                          onClick={() => handleToggleActive(member)}
                          className="text-xs text-ink-400 hover:text-brand inline-flex items-center gap-1"
                        >
                          {member.is_active ? <FiUserX size={13} /> : <FiUserCheck size={13} />}
                          {member.is_active ? "Deactivate" : "Activate"}
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
