import { api } from "./api";

export const projectService = {
  list: (params = {}) => api.get("/projects", { params }).then((r) => r.data),
  get: (id) => api.get(`/projects/${id}`).then((r) => r.data),
  create: (payload) => api.post("/projects", payload).then((r) => r.data),
  update: (id, payload) => api.put(`/projects/${id}`, payload).then((r) => r.data),
  remove: (id) => api.delete(`/projects/${id}`).then((r) => r.data),
  archive: (id) => api.post(`/projects/${id}/archive`).then((r) => r.data),
  restore: (id) => api.post(`/projects/${id}/restore`).then((r) => r.data),
  addMember: (id, user_id) => api.post(`/projects/${id}/members`, { user_id }).then((r) => r.data),
  removeMember: (id, userId) => api.delete(`/projects/${id}/members/${userId}`).then((r) => r.data),
};

export const taskService = {
  list: (params = {}) => api.get("/tasks", { params }).then((r) => r.data),
  get: (id) => api.get(`/tasks/${id}`).then((r) => r.data),
  board: (projectId) => api.get(`/tasks/board/${projectId}`).then((r) => r.data),
  create: (payload) => api.post("/tasks", payload).then((r) => r.data),
  update: (id, payload) => api.put(`/tasks/${id}`, payload).then((r) => r.data),
  updateStatus: (id, status, position) => api.patch(`/tasks/${id}/status`, { status, position }).then((r) => r.data),
  remove: (id) => api.delete(`/tasks/${id}`).then((r) => r.data),
  createSubtask: (id, payload) => api.post(`/tasks/${id}/subtasks`, payload).then((r) => r.data),
  subtasks: (id) => api.get(`/tasks/${id}/subtasks`).then((r) => r.data),
};

export const tagService = {
  list: () => api.get("/tags").then((r) => r.data),
  create: (payload) => api.post("/tags", payload).then((r) => r.data),
  remove: (id) => api.delete(`/tags/${id}`).then((r) => r.data),
};

export const commentService = {
  list: (taskId) => api.get(`/tasks/${taskId}/comments`).then((r) => r.data),
  create: (taskId, content) => api.post(`/tasks/${taskId}/comments`, { content }).then((r) => r.data),
  update: (commentId, content) => api.put(`/comments/${commentId}`, { content }).then((r) => r.data),
  remove: (commentId) => api.delete(`/comments/${commentId}`).then((r) => r.data),
};

export const fileService = {
  uploadToTask: (taskId, file) => {
    const form = new FormData();
    form.append("file", file);
    form.append("task_id", taskId);
    return api.post("/files/upload", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data);
  },
  uploadToProject: (projectId, file) => {
    const form = new FormData();
    form.append("file", file);
    form.append("project_id", projectId);
    return api.post("/files/upload", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data);
  },
  listForTask: (taskId) => api.get(`/files/task/${taskId}`).then((r) => r.data),
  listForProject: (projectId) => api.get(`/files/project/${projectId}`).then((r) => r.data),
  remove: (id) => api.delete(`/files/${id}`).then((r) => r.data),
  downloadUrl: (id) => `${api.defaults.baseURL}/files/${id}/download`,
};

export const userService = {
  list: (role) => api.get("/users", { params: role ? { role } : {} }).then((r) => r.data),
  get: (id) => api.get(`/users/${id}`).then((r) => r.data),
  updateProfile: (payload) => api.put("/users/me", payload).then((r) => r.data),
  changePassword: (payload) => api.put("/users/me/password", payload).then((r) => r.data),
  updateRole: (id, role) => api.put(`/users/${id}/role`, { role }).then((r) => r.data),
  deactivate: (id) => api.put(`/users/${id}/deactivate`).then((r) => r.data),
  activate: (id) => api.put(`/users/${id}/activate`).then((r) => r.data),
  online: () => api.get("/users/online").then((r) => r.data),
};

export const notificationService = {
  list: (unreadOnly = false) => api.get("/notifications", { params: { unread_only: unreadOnly } }).then((r) => r.data),
  unreadCount: () => api.get("/notifications/unread-count").then((r) => r.data),
  markRead: (id) => api.put(`/notifications/${id}/read`).then((r) => r.data),
  markAllRead: () => api.put("/notifications/read-all").then((r) => r.data),
  remove: (id) => api.delete(`/notifications/${id}`).then((r) => r.data),
};

export const dashboardService = {
  summary: () => api.get("/dashboard/summary").then((r) => r.data),
  recentActivity: (limit = 10) => api.get("/dashboard/recent-activity", { params: { limit } }).then((r) => r.data),
  teamPerformance: () => api.get("/dashboard/team-performance").then((r) => r.data),
  projectProgress: () => api.get("/dashboard/project-progress").then((r) => r.data),
};

export const reportService = {
  taskCompletion: (weeks = 8) => api.get("/reports/task-completion", { params: { weeks } }).then((r) => r.data),
  deadlineAnalysis: () => api.get("/reports/deadline-analysis").then((r) => r.data),
  exportUrl: (format) => `${api.defaults.baseURL}/reports/export/${format}`,
};

export const calendarService = {
  tasks: (start, end) => api.get("/calendar/tasks", { params: { start, end } }).then((r) => r.data),
};

export const timeLogService = {
  start: (task_id) => api.post("/time-logs/start", { task_id }).then((r) => r.data),
  stop: (logId) => api.post(`/time-logs/${logId}/stop`).then((r) => r.data),
  running: () => api.get("/time-logs/running").then((r) => r.data),
  forTask: (taskId) => api.get(`/time-logs/task/${taskId}`).then((r) => r.data),
  timesheet: (params = {}) => api.get("/time-logs/timesheet", { params }).then((r) => r.data),
};

export const aiService = {
  suggestPriority: (payload) => api.post("/ai/suggest-priority", payload).then((r) => r.data),
  predictDeadline: (taskId) => api.get(`/ai/predict-deadline/${taskId}`).then((r) => r.data),
  workloadDistribution: (projectId) => api.get(`/ai/workload-distribution/${projectId}`).then((r) => r.data),
  projectInsights: (projectId) => api.get(`/ai/project-insights/${projectId}`).then((r) => r.data),
  summarizeTask: (taskId) => api.post(`/ai/summarize-task/${taskId}`).then((r) => r.data),
};

export const auditService = {
  list: (params = {}) => api.get("/audit", { params }).then((r) => r.data),
  loginHistory: (params = {}) => api.get("/audit/login-history", { params }).then((r) => r.data),
};
