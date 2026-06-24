import React, { useEffect, useState } from "react";
import { Modal } from "../common/Modal";
import { Spinner } from "../common/Primitives";
import { taskService, userService, projectService } from "../../services/domainServices";
import { useToast } from "../../context/ToastContext";
import { apiErrorMessage } from "../../services/api";

const emptyForm = { title: "", description: "", priority: "medium", status: "todo", project_id: "", assigned_to: "", due_date: "" };

export function NewTaskModal({ open, onClose, onCreated, defaultProjectId, defaultStatus }) {
  const [form, setForm] = useState(emptyForm);
  const [projects, setProjects] = useState([]);
  const [members, setMembers] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    if (!open) return;
    setForm({
      ...emptyForm,
      project_id: defaultProjectId || "",
      status: defaultStatus || "todo",
    });
    projectService.list().then(setProjects);
    userService.list().then(setMembers);
  }, [open, defaultProjectId, defaultStatus]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.project_id) {
      showToast("Choose a project first.", "error");
      return;
    }
    setSubmitting(true);
    try {
      const task = await taskService.create({
        ...form,
        project_id: Number(form.project_id),
        assigned_to: form.assigned_to ? Number(form.assigned_to) : null,
        due_date: form.due_date ? new Date(form.due_date).toISOString() : null,
      });
      showToast("Task created.", "success");
      onCreated?.(task);
      onClose();
    } catch (error) {
      showToast(apiErrorMessage(error, "Could not create task."), "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="New task"
      footer={
        <>
          <button className="btn-ghost" onClick={onClose}>Cancel</button>
          <button form="new-task-form" type="submit" className="btn-primary" disabled={submitting}>
            {submitting && <Spinner className="h-4 w-4" />} Create task
          </button>
        </>
      }
    >
      <form id="new-task-form" onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label">Title</label>
          <input className="input" required value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} autoFocus />
        </div>
        <div>
          <label className="label">Description</label>
          <textarea className="input min-h-[70px]" value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Project</label>
            <select className="input" required value={form.project_id} onChange={(e) => setForm((f) => ({ ...f, project_id: e.target.value }))}>
              <option value="">Select a project</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Assignee</label>
            <select className="input" value={form.assigned_to} onChange={(e) => setForm((f) => ({ ...f, assigned_to: e.target.value }))}>
              <option value="">Unassigned</option>
              {members.map((m) => <option key={m.id} value={m.id}>{m.username}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Priority</label>
            <select className="input" value={form.priority} onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}>
              {["low", "medium", "high", "critical"].map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Due date</label>
            <input type="date" className="input" value={form.due_date} onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))} />
          </div>
        </div>
      </form>
    </Modal>
  );
}
