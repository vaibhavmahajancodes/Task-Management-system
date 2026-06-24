import React, { useEffect, useState } from "react";
import { auditService } from "../services/domainServices";
import { Spinner, EmptyState } from "../components/common/Primitives";
import { formatDistanceToNow } from "date-fns";

export default function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const PAGE_SIZE = 30;

  const load = () => {
    setLoading(true);
    auditService
      .list({ page, page_size: PAGE_SIZE, search: search || undefined })
      .then((data) => {
        setLogs(data.items || []);
        setTotal(data.total || 0);
      })
      .finally(() => setLoading(false));
  };

  useEffect(load, [page, search]); // eslint-disable-line react-hooks/exhaustive-deps

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Audit Log</h1>
        <p className="text-sm text-ink-400 dark:text-ink-100">
          A full record of every action taken across the platform.
        </p>
      </div>

      <div className="card p-4">
        <input
          className="input max-w-sm"
          placeholder="Filter by action or user..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
      </div>

      {loading ? (
        <div className="flex justify-center py-24">
          <Spinner className="h-7 w-7 text-brand" />
        </div>
      ) : logs.length === 0 ? (
        <EmptyState title="No audit entries found" />
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-ink-50/60 dark:bg-white/5 text-left text-xs text-ink-400">
              <tr>
                <th className="px-4 py-3 font-medium">Time</th>
                <th className="px-4 py-3 font-medium">User</th>
                <th className="px-4 py-3 font-medium">Action</th>
                <th className="px-4 py-3 font-medium hidden md:table-cell">Entity</th>
                <th className="px-4 py-3 font-medium hidden lg:table-cell">Details</th>
                <th className="px-4 py-3 font-medium hidden lg:table-cell">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-black/[0.06] dark:divide-white/[0.06]">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-ink-50/40 dark:hover:bg-white/[0.03]">
                  <td className="px-4 py-3 whitespace-nowrap text-ink-400">
                    {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                  </td>
                  <td className="px-4 py-3 font-medium">
                    {log.username || <span className="text-ink-400">system</span>}
                  </td>
                  <td className="px-4 py-3">
                    <code className="text-xs bg-ink-50 dark:bg-white/5 px-1.5 py-0.5 rounded font-mono">
                      {log.action}
                    </code>
                  </td>
                  <td className="px-4 py-3 hidden md:table-cell text-ink-400">
                    {log.entity_type && `${log.entity_type} #${log.entity_id}`}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell text-ink-400 max-w-xs truncate">
                    {log.details}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell text-ink-400 font-mono text-xs">
                    {log.ip_address}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-black/[0.06] dark:border-white/[0.06] text-xs text-ink-400">
              <span>Page {page} of {totalPages} ({total} entries)</span>
              <div className="flex gap-2">
                <button className="btn-ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                  Previous
                </button>
                <button className="btn-ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
