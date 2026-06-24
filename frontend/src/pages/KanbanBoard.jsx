import React, { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { FiPlus, FiArrowLeft, FiAlertCircle } from "react-icons/fi";
import { taskService, projectService } from "../services/domainServices";
import { Spinner, Avatar, PriorityBadge } from "../components/common/Primitives";
import { NewTaskModal } from "../components/tasks/NewTaskModal";
import { TaskDetailModal } from "../components/tasks/TaskDetailModal";
import { useBoardSocket } from "../hooks/useBoardSocket";
import { useToast } from "../context/ToastContext";

const COLUMNS = [
  { key: "todo", label: "To Do", accent: "#94A3B8" },
  { key: "in_progress", label: "In Progress", accent: "#E8A33D" },
  { key: "review", label: "Review", accent: "#2F6F5E" },
  { key: "completed", label: "Done", accent: "#1B4940" },
];

function priorityColor(priority) {
  return { low: "#94A3B8", medium: "#2F6F5E", high: "#E8A33D", critical: "#DC2626" }[priority] || "#94A3B8";
}

function TaskCard({ task, index, onOpen }) {
  return (
    <Draggable draggableId={String(task.id)} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={() => onOpen(task.id)}
          className={"card p-3 mb-2 cursor-pointer hover:shadow-popover transition-shadow border-l-4 " + (snapshot.isDragging ? "kanban-dragging shadow-popover" : "")}
          style={{ borderLeftColor: priorityColor(task.priority), ...provided.draggableProps.style }}
        >
          <p className="text-sm font-medium mb-2 line-clamp-2">{task.title}</p>
          <div className="flex flex-wrap gap-1 mb-2">
            {task.tags?.map((t) => (
              <span key={t.id} className="badge text-[10px]" style={{ backgroundColor: t.color + "22", color: t.color }}>
                {t.name}
              </span>
            ))}
          </div>
          <div className="flex items-center justify-between">
            <PriorityBadge priority={task.priority} />
            {task.assignee && <Avatar user={task.assignee} size="sm" />}
          </div>
          {task.is_overdue && (
            <p className="flex items-center gap-1 text-xs text-critical mt-2">
              <FiAlertCircle size={12} /> Overdue
            </p>
          )}
        </div>
      )}
    </Draggable>
  );
}

export default function KanbanBoard() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [board, setBoard] = useState({ todo: [], in_progress: [], review: [], completed: [] });
  const [loading, setLoading] = useState(true);
  const [newTaskOpen, setNewTaskOpen] = useState(false);
  const [newTaskStatus, setNewTaskStatus] = useState("todo");
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const { showToast } = useToast();

  const load = useCallback(() => {
    setLoading(true);
    Promise.all([projectService.get(projectId), taskService.board(projectId)])
      .then(([p, b]) => {
        setProject(p);
        setBoard(b);
      })
      .finally(() => setLoading(false));
  }, [projectId]);

  useEffect(load, [load]);

  useBoardSocket(projectId, (payload) => {
    if (["task_created", "task_updated", "task_moved", "task_deleted"].includes(payload.event)) {
      load();
    }
  });

  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    const sourceCol = source.droppableId;
    const destCol = destination.droppableId;

    setBoard((prev) => {
      const next = { ...prev };
      const sourceItems = Array.from(next[sourceCol]);
      const moved = sourceItems.splice(source.index, 1)[0];
      next[sourceCol] = sourceItems;
      const destItems = sourceCol === destCol ? sourceItems : Array.from(next[destCol]);
      destItems.splice(destination.index, 0, { ...moved, status: destCol });
      next[destCol] = destItems;
      return next;
    });

    try {
      await taskService.updateStatus(Number(draggableId), destCol, destination.index);
    } catch {
      showToast("Could not move task. Refreshing board.", "error");
      load();
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-7 w-7 text-brand" />
      </div>
    );
  }

  return (
    <div className="space-y-5 h-full flex flex-col">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Link to={"/projects/" + projectId} className="p-2 rounded-lg hover:bg-ink-50 dark:hover:bg-white/5">
            <FiArrowLeft size={18} />
          </Link>
          <div className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-full" style={{ backgroundColor: project?.color }} />
            <h1 className="font-display text-xl font-semibold">{project?.name} board</h1>
          </div>
        </div>
        <button
          className="btn-primary"
          onClick={() => {
            setNewTaskStatus("todo");
            setNewTaskOpen(true);
          }}
        >
          <FiPlus size={16} /> New task
        </button>
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 flex-1 overflow-x-auto">
          {COLUMNS.map((col) => (
            <Droppable droppableId={col.key} key={col.key}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={"rounded-xl p-3 flex flex-col min-h-[200px] bg-ink-50/50 dark:bg-white/[0.03] " + (snapshot.isDraggingOver ? "ring-2 ring-brand/40" : "")}
                >
                  <div className="flex items-center justify-between mb-3 px-1">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: col.accent }} />
                      <span className="text-sm font-semibold">{col.label}</span>
                      <span className="text-xs text-ink-400">{board[col.key]?.length || 0}</span>
                    </div>
                    <button
                      onClick={() => {
                        setNewTaskStatus(col.key);
                        setNewTaskOpen(true);
                      }}
                      className="text-ink-400 hover:text-brand p-1"
                      aria-label={"Add task to " + col.label}
                    >
                      <FiPlus size={14} />
                    </button>
                  </div>
                  <div className="flex-1">
                    {(board[col.key] || []).map((task, index) => (
                      <TaskCard key={task.id} task={task} index={index} onOpen={setSelectedTaskId} />
                    ))}
                    {provided.placeholder}
                  </div>
                </div>
              )}
            </Droppable>
          ))}
        </div>
      </DragDropContext>

      <NewTaskModal
        open={newTaskOpen}
        onClose={() => setNewTaskOpen(false)}
        onCreated={load}
        defaultProjectId={projectId}
        defaultStatus={newTaskStatus}
      />
      <TaskDetailModal taskId={selectedTaskId} open={!!selectedTaskId} onClose={() => setSelectedTaskId(null)} onChanged={load} />
    </div>
  );
}
