import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { FiTrello, FiUserPlus, FiX, FiCpu, FiPaperclip, FiUpload } from "react-icons/fi";
import { projectService, taskService, userService, fileService, aiService } from "../services/domainServices";
import { Spinner, EmptyState, Avatar, PriorityBadge, StatusBadge } from "../components/common/Primitives";
import { Modal } from "../components/common/Modal";
import { useToast } from "../context/ToastContext";
import { apiErrorMessage } from "../services/api";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [insight, setInsight] = useState(null);
  const [insightLoading, setInsightLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [addMemberOpen, setAddMemberOpen] = useState(false);
  const [allUsers, setAllUsers] = useState([]);
  const { showToast } = useToast();

  const load = async () => {
    setLoading(true);
    try {
      const [p, t, files] = await Promise.all([
        projectService.get(projectId),
        taskService.list({ project_id: projectId, page_size: 50 }),
        fileService.listForProject(projectId),
      ]);
      setProject(p);
      setTasks(t.items || []);
      setAttachments(files);
    } catch (error) {
      showToast(apiErrorMessage(error, "Could not load project."), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  const loadInsight = async () => {
    setInsightLoading(true);
    try {
      const data = await aiService.projectInsights(projectId);
      setInsight(data);
    } catch (error) {
      showToast(apiErrorMessage(error, "Could not generate insights."), "error");
    } finally {
      setInsightLoading(false);
    }
  };

  const openAddMember = async () => {
    const users = await userService.list();
    setAllUsers(users);
    setAddMemberOpen(true);
  };

  const handleAddMember = async (userId) => {
    try {
      const updated = await projectService.addMember(projectId, userId);
      setProject(updated);
      showToast("Member added.", "success");
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  const handleRemoveMember = async (userId) => {
    try {
      const updated = await projectService.removeMember(projectId, userId);
      setProject(updated);
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const attachment = await fileService.uploadToProject(projectId, file);
      setAttachments((prev) => [attachment, ...prev]);
      showToast("File uploaded.", "success");
    } catch (error) {
      showToast(apiErrorMessage(error, "Upload failed."), "error");
    }
    e.target.value = "";
  };

  if (loading || !project) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-7 w-7 text-brand" />
      </div>
    );
  }

  const memberIds = new Set(project.members.map((m) => m.id));
  const availableUsers = allUsers.filter((u) => !memberIds.has(u.id) && u.id !== project.owner_id);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="h-4 w-4 rounded-full" style={{ backgroundColor: project.color }} />
          <div>
            <h1 className="font-display text-2xl font-semibold">{project.name}</h1>
            <p className="text-sm text-ink-400 dark:text-ink-100">{project.description || "No description yet."}</p>
          </div>
        </div>
        <Link to={`/projects/${projectId}/board`} className="btn-primary">
          <FiTrello size={16} /> Open board
        </Link>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <StatusBadge status={project.status} />
        <PriorityBadge priority={project.priority} />
        {project.deadline && <span className="badge bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100">Due {project.deadline}</span>}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-display font-semibold">Tasks ({tasks.length})</h2>
          </div>
          {tasks.length === 0 ? (
            <EmptyState title="No tasks yet" description="Open the Kanban board to add the first task." />
          ) : (
            <ul className="divide-y divide-black/[0.06] dark:divide-white/[0.06]">
              {tasks.map((t) => (
                <li key={t.id} className="py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium truncate">{t.title}</p>
                    <p className="text-xs text-ink-400">{t.assignee ? t.assignee.username : "Unassigned"}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <PriorityBadge priority={t.priority} />
                    <StatusBadge status={t.status} />
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="space-y-4">
          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-display font-semibold">Team</h2>
              <button onClick={openAddMember} className="text-brand text-xs flex items-center gap-1 hover:underline">
                <FiUserPlus size={14} /> Add
              </button>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Avatar user={project.owner} size="sm" />
                <span className="text-sm">{project.owner.username}</span>
                <span className="badge bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100 ml-auto">Owner</span>
              </div>
              {project.members.map((m) => (
                <div key={m.id} className="flex items-center gap-2">
                  <Avatar user={m} size="sm" />
                  <span className="text-sm">{m.username}</span>
                  <button onClick={() => handleRemoveMember(m.id)} className="ml-auto text-ink-400 hover:text-critical">
                    <FiX size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-display font-semibold flex items-center gap-1.5">
                <FiCpu size={15} className="text-brand" /> AI insights
              </h2>
              <button onClick={loadInsight} className="text-brand text-xs hover:underline" disabled={insightLoading}>
                {insightLoading ? "Generating..." : "Generate"}
              </button>
            </div>
            {insight ? (
              <div className="space-y-2">
                <p className="text-sm">{insight.summary}</p>
                <ul className="text-xs text-ink-400 list-disc pl-4 space-y-1">
                  {insight.highlights.map((h) => <li key={h}>{h}</li>)}
                </ul>
              </div>
            ) : (
              <p className="text-xs text-ink-400">Generate a quick status summary from current task data.</p>
            )}
          </div>

          <div className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-display font-semibold flex items-center gap-1.5">
                <FiPaperclip size={15} /> Files
              </h2>
              <label className="text-brand text-xs flex items-center gap-1 hover:underline cursor-pointer">
                <FiUpload size={14} /> Upload
                <input type="file" className="hidden" onChange={handleFileUpload} />
              </label>
            </div>
            {attachments.length === 0 ? (
              <p className="text-xs text-ink-400">No documents uploaded yet.</p>
            ) : (
              <ul className="space-y-1.5">
                {attachments.map((a) => (
                  <li key={a.id}>
                    <a href={fileService.downloadUrl(a.id)} className="text-sm text-brand hover:underline truncate block">
                      {a.original_name}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      <Modal open={addMemberOpen} onClose={() => setAddMemberOpen(false)} title="Add team member">
        {availableUsers.length === 0 ? (
          <p className="text-sm text-ink-400">Everyone is already on this project.</p>
        ) : (
          <ul className="space-y-1">
            {availableUsers.map((u) => (
              <li key={u.id}>
                <button
                  onClick={() => {
                    handleAddMember(u.id);
                    setAddMemberOpen(false);
                  }}
                  className="w-full flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-ink-50 dark:hover:bg-white/5 text-left"
                >
                  <Avatar user={u} size="sm" />
                  <span className="text-sm">{u.full_name || u.username}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </Modal>
    </div>
  );
}
