import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FiPlus, FiArchive, FiFolder } from "react-icons/fi";
import { projectService } from "../services/domainServices";
import { Spinner, EmptyState, PriorityBadge, StatusBadge } from "../components/common/Primitives";
import { Modal } from "../components/common/Modal";
import { useToast } from "../context/ToastContext";
import { apiErrorMessage } from "../services/api";

const STATUS_OPTIONS = ["planning", "active", "on_hold", "completed", "archived"];
const PRIORITY_OPTIONS = ["low", "medium", "high", "critical"];

function ProjectFormFields({ form, setForm }) {
  return (
    <div className="space-y-4">
      <div>
        <label className="label" htmlFor="p-name">Project name</label>
        <input
          id="p-name"
          className="input"
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          required
        />
      </div>
      <div>
        <label className="label" htmlFor="p-desc">Description</label>
        <textarea
          id="p-desc"
          className="input min-h-[80px]"
          value={form.description}
          onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label" htmlFor="p-status">Status</label>
          <select
            id="p-status"
            className="input"
            value={form.status}
            onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s.replace("_", " ")}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="p-priority">Priority</label>
          <select
            id="p-priority"
            className="input"
            value={form.priority}
            onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
          >
            {PRIORITY_OPTIONS.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label" htmlFor="p-deadline">Deadline</label>
          <input
            id="p-deadline"
            type="date"
            className="input"
            value={form.deadline}
            onChange={(e) => setForm((f) => ({ ...f, deadline: e.target.value }))}
          />
        </div>
        <div>
          <label className="label" htmlFor="p-color">Accent color</label>
          <input
            id="p-color"
            type="color"
            className="input h-10 p-1"
            value={form.color}
            onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
          />
        </div>
      </div>
    </div>
  );
}

const emptyForm = { name: "", description: "", status: "planning", priority: "medium", deadline: "", color: "#2F6F5E" };

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showArchived, setShowArchived] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const { showToast } = useToast();

  const load = () => {
    setLoading(true);
    projectService
      .list({ is_archived: showArchived })
      .then(setProjects)
      .finally(() => setLoading(false));
  };

  useEffect(load, [showArchived]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await projectService.create({ ...form, deadline: form.deadline || null });
      showToast("Project created.", "success");
      setModalOpen(false);
      setForm(emptyForm);
      load();
    } catch (error) {
      showToast(apiErrorMessage(error, "Could not create project."), "error");
    } finally {
      setSubmitting(false);
    }
  };

  const handleArchive = async (project) => {
    try {
      if (project.is_archived) await projectService.restore(project.id);
      else await projectService.archive(project.id);
      load();
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold">Projects</h1>
          <p className="text-sm text-ink-400 dark:text-ink-100">Organize your team's work into focused projects.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            className={`btn-secondary text-xs ${showArchived ? "ring-1 ring-brand" : ""}`}
            onClick={() => setShowArchived((s) => !s)}
          >
            <FiArchive size={14} /> {showArchived ? "Showing archived" : "Show archived"}
          </button>
          <button className="btn-primary" onClick={() => setModalOpen(true)}>
            <FiPlus size={16} /> New project
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-24">
          <Spinner className="h-7 w-7 text-brand" />
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          icon={<FiFolder />}
          title="No projects yet"
          description="Create your first project to start organizing tasks for your team."
          action={
            <button className="btn-primary" onClick={() => setModalOpen(true)}>
              <FiPlus size={16} /> New project
            </button>
          }
        />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((p) => (
            <div key={p.id} className="card p-5 flex flex-col gap-3 hover:shadow-popover transition-shadow">
              <div className="flex items-start justify-between">
                <Link to={`/projects/${p.id}`} className="flex items-center gap-2 min-w-0">
                  <span className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: p.color }} />
                  <span className="font-display font-semibold truncate hover:text-brand transition-colors">{p.name}</span>
                </Link>
                <button
                  onClick={() => handleArchive(p)}
                  className="text-ink-400 hover:text-critical p-1 rounded"
                  title={p.is_archived ? "Restore project" : "Archive project"}
                >
                  <FiArchive size={15} />
                </button>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                <StatusBadge status={p.status} />
                <PriorityBadge priority={p.priority} />
              </div>

              <div>
                <div className="flex items-center justify-between text-xs text-ink-400 mb-1">
                  <span>{p.task_count} task{p.task_count === 1 ? "" : "s"}</span>
                  <span>{p.progress_percent}%</span>
                </div>
                <div className="h-1.5 rounded-full bg-ink-50 dark:bg-white/5 overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${p.progress_percent}%`, backgroundColor: p.color }} />
                </div>
              </div>

              {p.deadline && <p className="text-xs text-ink-400">Due {p.deadline}</p>}

              <div className="flex gap-2 mt-1">
                <Link to={`/projects/${p.id}`} className="btn-secondary flex-1 text-xs">Details</Link>
                <Link to={`/projects/${p.id}/board`} className="btn-secondary flex-1 text-xs">Board</Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="New project"
        footer={
          <>
            <button className="btn-ghost" onClick={() => setModalOpen(false)}>Cancel</button>
            <button form="create-project-form" type="submit" className="btn-primary" disabled={submitting}>
              {submitting && <Spinner className="h-4 w-4" />} Create project
            </button>
          </>
        }
      >
        <form id="create-project-form" onSubmit={handleCreate}>
          <ProjectFormFields form={form} setForm={setForm} />
        </form>
      </Modal>
    </div>
  );
}
