import React, { useEffect, useState } from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar, Legend } from "recharts";
import { FiDownload } from "react-icons/fi";
import { reportService, dashboardService } from "../services/domainServices";
import { Spinner, EmptyState } from "../components/common/Primitives";

export default function Reports() {
  const [completion, setCompletion] = useState([]);
  const [deadlines, setDeadlines] = useState([]);
  const [teamPerformance, setTeamPerformance] = useState([]);
  const [projectProgress, setProjectProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      reportService.taskCompletion(8),
      reportService.deadlineAnalysis(),
      dashboardService.teamPerformance(),
      dashboardService.projectProgress(),
    ])
      .then(([c, d, t, p]) => {
        setCompletion(c);
        setDeadlines(d);
        setTeamPerformance(t);
        setProjectProgress(p);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center py-24">
        <Spinner className="h-7 w-7 text-brand" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl font-semibold">Reports</h1>
          <p className="text-sm text-ink-400 dark:text-ink-100">Completion trends, productivity, and deadline risk.</p>
        </div>
        <div className="flex gap-2">
          <a className="btn-secondary text-xs" href={reportService.exportUrl("csv")}><FiDownload size={13} /> CSV</a>
          <a className="btn-secondary text-xs" href={reportService.exportUrl("excel")}><FiDownload size={13} /> Excel</a>
          <a className="btn-secondary text-xs" href={reportService.exportUrl("pdf")}><FiDownload size={13} /> PDF</a>
        </div>
      </div>

      <div className="card p-5">
        <h2 className="font-display font-semibold mb-4">Task completion trend</h2>
        {completion.length === 0 ? (
          <EmptyState title="Not enough data yet" />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={completion}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" className="text-ink-100 dark:text-white/10" />
              <XAxis dataKey="period" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="completed" stroke="#2F6F5E" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="created" stroke="#E8A33D" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">Team productivity</h2>
          {teamPerformance.length === 0 ? (
            <EmptyState title="No assigned tasks yet" />
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-ink-400">
                <tr>
                  <th className="py-2 font-medium">Member</th>
                  <th className="py-2 font-medium text-right">Assigned</th>
                  <th className="py-2 font-medium text-right">Completed</th>
                  <th className="py-2 font-medium text-right">Overdue</th>
                  <th className="py-2 font-medium text-right">Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/[0.06] dark:divide-white/[0.06]">
                {teamPerformance.map((u) => (
                  <tr key={u.user_id}>
                    <td className="py-2">{u.full_name || u.username}</td>
                    <td className="py-2 text-right">{u.assigned_count}</td>
                    <td className="py-2 text-right">{u.completed_count}</td>
                    <td className="py-2 text-right text-critical">{u.overdue_count}</td>
                    <td className="py-2 text-right font-medium">{u.completion_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card p-5">
          <h2 className="font-display font-semibold mb-4">Deadline analysis by project</h2>
          {deadlines.length === 0 ? (
            <EmptyState title="No projects yet" />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={deadlines} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="currentColor" className="text-ink-100 dark:text-white/10" />
                <XAxis type="number" tick={{ fontSize: 11 }} allowDecimals={false} />
                <YAxis type="category" dataKey="project_name" width={110} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="on_time" stackId="a" fill="#2F6F5E" name="On time" />
                <Bar dataKey="upcoming" stackId="a" fill="#CFE5DD" name="Upcoming" />
                <Bar dataKey="overdue" stackId="a" fill="#DC2626" name="Overdue" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card p-5">
        <h2 className="font-display font-semibold mb-4">Project progress</h2>
        {projectProgress.length === 0 ? (
          <EmptyState title="No active projects yet" />
        ) : (
          <div className="space-y-3">
            {projectProgress.map((p) => (
              <div key={p.project_id}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium">{p.project_name}</span>
                  <span className="text-ink-400">{p.completed_tasks}/{p.total_tasks} ({p.progress_percent}%)</span>
                </div>
                <div className="h-2 rounded-full bg-ink-50 dark:bg-white/5 overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${p.progress_percent}%`, backgroundColor: p.color }} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
