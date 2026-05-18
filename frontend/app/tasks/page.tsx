"use client";

import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

export default function TasksPage() {
  const { data: tasks, loading, error } = useApi<any[]>("/api/tasks", []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Task Manager</h1>
      {loading ? <LoadingCard label="Loading tasks" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Tasks">
        <div className="overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[#8c96a6]"><tr><th className="p-2">ID</th><th>Status</th><th>Subagents</th><th>Message</th></tr></thead>
            <tbody className="text-[#30343b]">{tasks.map((task) => <tr key={task.id} className="border-t border-[#e4e9f0]"><td className="p-2">{task.id}</td><td>{task.status}</td><td>{task.assigned_subagents?.length || 0}</td><td>{task.message}</td></tr>)}</tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
