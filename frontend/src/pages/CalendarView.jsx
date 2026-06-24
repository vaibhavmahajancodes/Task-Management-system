import React, { useEffect, useMemo, useState } from "react";
import Calendar from "react-calendar";
import { startOfMonth, endOfMonth, startOfWeek, endOfWeek, format, isSameDay } from "date-fns";
import { calendarService } from "../services/domainServices";
import { PriorityBadge, Spinner, EmptyState } from "../components/common/Primitives";
import { TaskDetailModal } from "../components/tasks/TaskDetailModal";

const VIEWS = ["month", "week", "day"];

export default function CalendarView() {
  const [view, setView] = useState("month");
  const [date, setDate] = useState(new Date());
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTaskId, setSelectedTaskId] = useState(null);

  const range = useMemo(() => {
    if (view === "month") return { start: startOfMonth(date), end: endOfMonth(date) };
    if (view === "week") return { start: startOfWeek(date), end: endOfWeek(date) };
    return { start: date, end: date };
  }, [view, date]);

  useEffect(() => {
    setLoading(true);
    calendarService
      .tasks(range.start.toISOString(), range.end.toISOString())
      .then(setTasks)
      .finally(() => setLoading(false));
  }, [range.start, range.end]); // eslint-disable-line react-hooks/exhaustive-deps

  const tasksByDay = (day) => tasks.filter((t) => t.due_date && isSameDay(new Date(t.due_date), day));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold">Calendar</h1>
          <p className="text-sm text-ink-400 dark:text-ink-100">See every deadline across your projects at a glance.</p>
        </div>
        <div className="flex gap-1 bg-ink-50 dark:bg-white/5 rounded-lg p-1">
          {VIEWS.map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium capitalize ${
                view === v ? "bg-surface-card dark:bg-surface-darkcard shadow-sm" : "text-ink-400"
              }`}
            >
              {v}
            </button>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-4 lg:col-span-2">
          <Calendar
            onChange={setDate}
            value={date}
            className="w-full border-none font-body"
            tileContent={({ date: tileDate }) => {
              const dayTasks = tasksByDay(tileDate);
              if (dayTasks.length === 0) return null;
              return (
                <div className="flex justify-center gap-0.5 mt-1">
                  {dayTasks.slice(0, 3).map((t) => (
                    <span key={t.id} className="h-1.5 w-1.5 rounded-full bg-brand" />
                  ))}
                </div>
              );
            }}
          />
        </div>

        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">
            {view === "day" ? format(date, "MMMM d, yyyy") : `Tasks due ${format(range.start, "MMM d")} – ${format(range.end, "MMM d")}`}
          </h2>
          {loading ? (
            <div className="flex justify-center py-8"><Spinner className="h-6 w-6 text-brand" /></div>
          ) : tasks.length === 0 ? (
            <EmptyState title="Nothing due in this range" />
          ) : (
            <ul className="space-y-2 max-h-[420px] overflow-y-auto">
              {tasks
                .slice()
                .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
                .map((t) => (
                  <li key={t.id}>
                    <button
                      onClick={() => setSelectedTaskId(t.id)}
                      className="w-full text-left px-3 py-2 rounded-lg hover:bg-ink-50 dark:hover:bg-white/5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium truncate">{t.title}</span>
                        <PriorityBadge priority={t.priority} />
                      </div>
                      <p className="text-xs text-ink-400 mt-0.5">{format(new Date(t.due_date), "EEE, MMM d • h:mm a")}</p>
                    </button>
                  </li>
                ))}
            </ul>
          )}
        </div>
      </div>

      <TaskDetailModal taskId={selectedTaskId} open={!!selectedTaskId} onClose={() => setSelectedTaskId(null)} />
    </div>
  );
}
