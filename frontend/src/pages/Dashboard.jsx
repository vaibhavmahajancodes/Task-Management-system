import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { FiFolder, FiCheckCircle, FiClock, FiAlertCircle } from "react-icons/fi";
import { dashboardService } from "../services/domainServices";
import { Spinner, EmptyState } from "../components/common/Primitives";
import { formatDistanceToNow } from "date-fns";

const PIE_COLORS = ["#2F6F5E", "#7FB3A3", "#E8A33D", "#DC2626"];

function StatCard({ icon: Icon, label, value, tone = "brand" }) {
  const tones = {
    brand: "bg-brand-50 text-brand-700 dark:bg-brand-900/40 dark:text-brand-300",
    amber: "bg-amber-100 text-amber-600",
    critical: "bg-critical-100 text-critical-500",
    ink: "bg-ink-50 text-ink-400 dark:bg-white/5 dark:text-ink-100",
  };
  return (
    <div className="card p-5 flex items-start justify-between">
      <div>
        <p className="text-xs font-medium text-ink-400 dark:text-ink-100 mb-1">{label}</p>
        <p className="font-display text-2xl font-semibold">{value}</p>
      </div>
      <div className={`h-9 w-9 rounded-lg flex items-center justify-center ${tones[tone]}`}>
        <Icon size={18} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [activity, setActivity] = useState([]);
  const [team, setTeam] = useState([]);
  const [projectProgress, setProjectProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([
      dashboardService.summary(),
      dashboardService.recentActivity(8),
      dashboardService.teamPerformance(),
      dashboardService.projectProgress(),
    ])
      .then(([s, a, t, p]) => {
        if (!active) return;
        setSummary(s);
        setActivity(a);
        setTeam(t);
        setProjectProgress(p);
      })
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-7 w-7 text-brand" />
      </div>
    );
  }

  const statusPieData = summary
    ? [
        { name: "Completed", value: summary.completed_tasks },
        { name: "Pending", value: summary.pending_tasks },
        { name: "Overdue", value: summary.overdue_tasks },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Dashboard</h1>
        <p className="text-sm text-ink-400 dark:text-ink-100">Here's how your projects and team are doing.</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FiFolder} label="Active Projects" value={summary.active_projects} tone="brand" />
        <StatCard icon={FiCheckCircle} label="Completed Tasks" value={summary.completed_tasks} tone="brand" />
        <StatCard icon={FiClock} label="Pending Tasks" value={summary.pending_tasks} tone="amber" />
        <StatCard icon={FiAlertCircle} label="Overdue Tasks" value={summary.overdue_tasks} tone="critical" />
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="card p-5 lg:col-span-2">
          <h2 className="font-display font-semibold mb-4">Project progress</h2>
          {projectProgress.length === 0 ? (
            <EmptyState title="No active projects yet" description="Create a project to see its progress here." />
          ) : (
            <div className="space-y-4">
              {projectProgress.slice(0, 6).map((p) => (
                <Link key={p.project_id} to={`/projects/${p.project_id}`} className="block group">
                  <div className="flex items-center justify-between text-sm mb-1.5">
                    <span className="font-medium group-hover:text-brand transition-colors">{p.project_name}</span>
                    <span className="text-ink-400">{p.progress_percent}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-ink-50 dark:bg-white/5 overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${p.progress_percent}%`, backgroundColor: p.color }}
                    />
                  </div>
                  {p.is_overdue && <p className="text-xs text-critical mt-1">Past deadline</p>}
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">Task breakdown</h2>
          {statusPieData.length === 0 ? (
            <EmptyState title="No tasks yet" />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={statusPieData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={75} paddingAngle={2}>
                  {statusPieData.map((entry, index) => (
                    <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
          <div className="flex flex-wrap gap-3 justify-center mt-2">
            {statusPieData.map((d, i) => (
              <div key={d.name} className="flex items-center gap-1.5 text-xs text-ink-400">
                <span className="h-2 w-2 rounded-full" style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }} />
                {d.name}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">Team performance</h2>
          {team.length === 0 ? (
            <EmptyState title="No assigned tasks yet" />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={team.slice(0, 6)}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" className="text-ink-100 dark:text-white/10" />
                <XAxis dataKey="username" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="completed_count" name="Completed" fill="#2F6F5E" radius={[4, 4, 0, 0]} />
                <Bar dataKey="assigned_count" name="Assigned" fill="#CFE5DD" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">Recent activity</h2>
          {activity.length === 0 ? (
            <EmptyState title="Nothing has happened yet" description="Activity will show up here as your team works." />
          ) : (
            <ul className="space-y-3 max-h-60 overflow-y-auto">
              {activity.map((a) => (
                <li key={a.id} className="text-sm flex justify-between gap-3">
                  <span className="text-ink-400 dark:text-ink-100">
                    <span className="font-medium text-ink dark:text-surface-light">{a.username || "Someone"}</span>{" "}
                    {a.details || a.action}
                  </span>
                  <span className="text-xs text-ink-400 whitespace-nowrap">
                    {formatDistanceToNow(new Date(a.created_at), { addSuffix: true })}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
