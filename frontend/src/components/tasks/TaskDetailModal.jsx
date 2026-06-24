import React, { useEffect, useState } from "react";
import { FiPlay, FiSquare, FiPaperclip, FiUpload, FiCpu } from "react-icons/fi";
import { Modal } from "../common/Modal";
import { Spinner, Avatar, PriorityBadge } from "../common/Primitives";
import {
  taskService,
  commentService,
  fileService,
  timeLogService,
  aiService,
  userService,
} from "../../services/domainServices";
import { useToast } from "../../context/ToastContext";
import { apiErrorMessage } from "../../services/api";
import { formatDistanceToNow } from "date-fns";

const STATUS_OPTIONS = ["todo", "in_progress", "review", "completed"];
const PRIORITY_OPTIONS = ["low", "medium", "high", "critical"];

export function TaskDetailModal({ taskId, open, onClose, onChanged }) {
  const [task, setTask] = useState(null);
  const [comments, setComments] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [subtasks, setSubtasks] = useState([]);
  const [members, setMembers] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [newSubtask, setNewSubtask] = useState("");
  const [runningLog, setRunningLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [suggestion, setSuggestion] = useState(null);
  const { showToast } = useToast();

  const load = async () => {
    if (!taskId) return;
    setLoading(true);
    try {
      const [t, c, files, sub, users, running] = await Promise.all([
        taskService.get(taskId),
        commentService.list(taskId),
        fileService.listForTask(taskId),
        taskService.subtasks(taskId),
        userService.list(),
        timeLogService.running().catch(() => null),
      ]);
      setTask(t);
      setComments(c);
      setAttachments(files);
      setSubtasks(sub);
      setMembers(users);
      setRunningLog(running && running.task_id === taskId ? running : null);
    } catch (error) {
      showToast(apiErrorMessage(error, "Could not load task."), "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId, open]);

  const patchTask = async (payload) => {
    try {
      const updated = await taskService.update(taskId, payload);
      setTask(updated);
      onChanged?.();
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    try {
      const c = await commentService.create(taskId, newComment.trim());
      setComments((prev) => [...prev, c]);
      setNewComment("");
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  const handleSubtask = async (e) => {
    e.preventDefault();
    if (!newSubtask.trim()) return;
    try {
      const st = await taskService.createSubtask(taskId, { title: newSubtask.trim(), project_id: task.project_id });
      setSubtasks((prev) => [...prev, st]);
      setNewSubtask("");
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const attachment = await fileService.uploadToTask(taskId, file);
      setAttachments((prev) => [attachment, ...prev]);
    } catch (error) {
      showToast(apiErrorMessage(error, "Upload failed."), "error");
    }
    e.target.value = "";
  };

  const toggleTimer = async () => {
    try {
      if (runningLog) {
        await timeLogService.stop(runningLog.id);
        setRunningLog(null);
      } else {
        const log = await timeLogService.start(taskId);
        setRunningLog(log);
      }
    } catch (error) {
      showToast(apiErrorMessage(error), "error");
    }
  };

  const handleSuggestPriority = async () => {
    try {
      const result = await aiService.suggestPriority({
        title: task.title,
        description: task.description,
        due_date: task.due_date,
      });
      setSuggestion(result);
    } catch (error) {
      showToast(apiErrorMessage(error, "Could not get a suggestion."), "error");
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={task ? task.title : "Task"} size="lg">
      {loading || !task ? (
        <div className="flex justify-center py-12">
          <Spinner className="h-6 w-6 text-brand" />
        </div>
      ) : (
        <div className="space-y-5">
          <textarea
            className="input min-h-[70px]"
            value={task.description || ""}
            placeholder="Add a description..."
            onChange={(e) => setTask((t) => ({ ...t, description: e.target.value }))}
            onBlur={(e) => patchTask({ description: e.target.value })}
          />

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div>
              <label className="label">Status</label>
              <select className="input" value={task.status} onChange={(e) => patchTask({ status: e.target.value })}>
                {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Priority</label>
              <select className="input" value={task.priority} onChange={(e) => patchTask({ priority: e.target.value })}>
                {PRIORITY_OPTIONS.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Assignee</label>
              <select
                className="input"
                value={task.assigned_to || ""}
                onChange={(e) => patchTask({ assigned_to: e.target.value ? Number(e.target.value) : null })}
              >
                <option value="">Unassigned</option>
                {members.map((m) => <option key={m.id} value={m.id}>{m.username}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Due date</label>
              <input
                type="date"
                className="input"
                value={task.due_date ? task.due_date.slice(0, 10) : ""}
                onChange={(e) => patchTask({ due_date: e.target.value ? new Date(e.target.value).toISOString() : null })}
              />
            </div>
          </div>

          <div className="flex items-center justify-between bg-ink-50 dark:bg-white/5 rounded-lg px-3 py-2">
            <button onClick={handleSuggestPriority} className="text-xs text-brand flex items-center gap-1.5 hover:underline">
              <FiCpu size={14} /> Suggest priority with AI
            </button>
            <button onClick={toggleTimer} className={`btn text-xs ${runningLog ? "bg-critical text-white" : "bg-brand text-white"}`}>
              {runningLog ? <FiSquare size={13} /> : <FiPlay size={13} />}
              {runningLog ? "Stop timer" : "Start timer"}
            </button>
          </div>
          {suggestion && (
            <p className="text-xs text-ink-400 -mt-3">
              Suggested: <PriorityBadge priority={suggestion.suggested_priority} /> — {suggestion.reasoning}
            </p>
          )}

          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold">Subtasks ({subtasks.length})</h3>
            </div>
            <ul className="space-y-1 mb-2">
              {subtasks.map((s) => (
                <li key={s.id} className="text-sm flex items-center gap-2 px-2 py-1.5 rounded-lg bg-ink-50/60 dark:bg-white/5">
                  <span className="flex-1">{s.title}</span>
                  <PriorityBadge priority={s.priority} />
                </li>
              ))}
            </ul>
            <form onSubmit={handleSubtask} className="flex gap-2">
              <input
                className="input"
                placeholder="Add a subtask..."
                value={newSubtask}
                onChange={(e) => setNewSubtask(e.target.value)}
              />
              <button type="submit" className="btn-secondary shrink-0">Add</button>
            </form>
          </div>

          <div>
            <h3 className="text-sm font-semibold mb-2 flex items-center gap-1.5"><FiPaperclip size={14} /> Attachments</h3>
            <ul className="space-y-1 mb-2">
              {attachments.map((a) => (
                <li key={a.id}>
                  <a href={fileService.downloadUrl(a.id)} className="text-sm text-brand hover:underline">{a.original_name}</a>
                </li>
              ))}
            </ul>
            <label className="btn-secondary text-xs inline-flex cursor-pointer">
              <FiUpload size={13} /> Upload file
              <input type="file" className="hidden" onChange={handleUpload} />
            </label>
          </div>

          <div>
            <h3 className="text-sm font-semibold mb-2">Comments ({comments.length})</h3>
            <ul className="space-y-3 max-h-48 overflow-y-auto mb-3">
              {comments.map((c) => (
                <li key={c.id} className="flex gap-2">
                  <Avatar user={c.user} size="sm" />
                  <div>
                    <p className="text-sm">
                      <span className="font-medium">{c.user.username}</span>{" "}
                      <span className="text-xs text-ink-400">{formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}</span>
                    </p>
                    <p className="text-sm text-ink-400 dark:text-ink-100">{c.content}</p>
                  </div>
                </li>
              ))}
            </ul>
            <form onSubmit={handleComment} className="flex gap-2">
              <input
                className="input"
                placeholder="Write a comment, @mention a teammate..."
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
              />
              <button type="submit" className="btn-primary shrink-0">Post</button>
            </form>
          </div>
        </div>
      )}
    </Modal>
  );
}
