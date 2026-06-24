import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { FiPlus, FiCheckSquare } from "react-icons/fi";
import { taskService, projectService, userService } from "../services/domainServices";
import { Spinner, EmptyState, Avatar, PriorityBadge, StatusBadge } from "../components/common/Primitives";
import { NewTaskModal } from "../components/tasks/NewTaskModal";
import { TaskDetailModal } from "../components/tasks/TaskDetailModal";

export default function Tasks() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [tasks, setTasks] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [members, setMembers] = useState([]);
  const [newTaskOpen, setNewTaskOpen] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState(null);

  const filters = {
    search: searchParams.get("search") || "",
    project_id: searchParams.get("project_id") || "",
    status: searchParams.get("status") || "",
    priority: searchParams.get("priority") || "",
    assigned_to: searchParams.get("assigned_to") || "",
  };

  const setFilter = (key, value) => {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next);
    setPage(1);
  };

  const load = () => {
    setLoading(true);
    const params = { page, page_size: 20 };
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params[k] = v;
    });
    taskService
      .list(params)
      .then((data) => {
        setTasks(data.items);
        setTotal(data.total);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, [searchParams, page]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    projectService.list().then(setProjects);
    userService.list().then(setMembers);
  }, []);

  const totalPages = Math.max(1, Math.ceil(total / 20));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold">Tasks</h1>
          <p className="text-sm text-ink-400 dark:text-ink-100">{total} task{total === 1 ? "" : "s"} across all your projects.</p>
        </div>
        <button className="btn-primary" onClick={() => setNewTaskOpen(true)}>
          <FiPlus size={16} /> New task
        </button>
      </div>

      <div className="card p-4 flex flex-wrap gap-3">
        <input
          className="input max-w-xs"
          placeholder="Search by title..."
          value={filters.search}
          onChange={(e) => setFilter("search", e.target.value)}
        />
        <select className="input max-w-[160px]" value={filters.project_id} onChange={(e) => setFilter("project_id", e.target.value)}>
          <option value="">All projects</option>
          {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        <select className="input max-w-[140px]" value={filters.status} onChange={(e) => setFilter("status", e.target.value)}>
          <option value="">All statuses</option>
          {["todo", "in_progress", "review", "completed"].map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
        </select>
        <select className="input max-w-[140px]" value={filters.priority} onChange={(e) => setFilter("priority", e.target.value)}>
          <option value="">All priorities</option>
          {["low", "medium", "high", "critical"].map((p) => <option key={p} value={p}>{p}</option>)}
        </select>
        <select className="input max-w-[160px]" value={filters.assigned_to} onChange={(e) => setFilter("assigned_to", e.target.value)}>
          <option value="">Everyone</option>
          {members.map((m) => <option key={m.id} value={m.id}>{m.username}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="flex justify-center py-24">
          <Spinner className="h-7 w-7 text-brand" />
        </div>
      ) : tasks.length === 0 ? (
        <EmptyState
          icon={<FiCheckSquare />}
          title="No tasks match these filters"
          description="Try clearing a filter, or create a new task."
          action={<button className="btn-primary" onClick={() => setNewTaskOpen(true)}><FiPlus size={16} /> New task</button>}
        />
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-ink-50/60 dark:bg-white/5 text-left text-xs text-ink-400">
              <tr>
                <th className="px-4 py-3 font-medium">Task</th>
                <th className="px-4 py-3 font-medium hidden sm:table-cell">Status</th>
                <th className="px-4 py-3 font-medium hidden sm:table-cell">Priority</th>
                <th className="px-4 py-3 font-medium hidden md:table-cell">Assignee</th>
                <th className="px-4 py-3 font-medium hidden md:table-cell">Due</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/[0.06] dark:divide-white/[0.06]">
              {tasks.map((t) => (
                <tr
                  key={t.id}
                  className="hover:bg-ink-50/40 dark:hover:bg-white/5 cursor-pointer"
                  onClick={() => setSelectedTaskId(t.id)}
                >
                  <td className="px-4 py-3">
                    <p className={`font-medium ${t.status === "completed" ? "line-through text-ink-400" : ""}`}>{t.title}</p>
                    {t.is_overdue && <span className="text-xs text-critical">Overdue</span>}
                  </td>
                  <td className="px-4 py-3 hidden sm:table-cell"><StatusBadge status={t.status} /></td>
                  <td className="px-4 py-3 hidden sm:table-cell"><PriorityBadge priority={t.priority} /></td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    {t.assignee ? (
                      <div className="flex items-center gap-2"><Avatar user={t.assignee} size="sm" /> {t.assignee.username}</div>
                    ) : (
                      <span className="text-ink-400">Unassigned</span>
                    )}
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell text-ink-400">
                    {t.due_date ? new Date(t.due_date).toLocaleDateString() : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-black/[0.06] dark:border-white/[0.06] text-xs text-ink-400">
              <span>Page {page} of {totalPages}</span>
              <div className="flex gap-2">
                <button className="btn-ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Previous</button>
                <button className="btn-ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</button>
              </div>
            </div>
          )}
        </div>
      )}

      <NewTaskModal open={newTaskOpen} onClose={() => setNewTaskOpen(false)} onCreated={load} />
      <TaskDetailModal taskId={selectedTaskId} open={!!selectedTaskId} onClose={() => setSelectedTaskId(null)} onChanged={load} />
    </div>
  );
}
