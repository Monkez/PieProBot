"use client";

import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { apiPost } from "@/lib/api";
import { useApi } from "@/lib/use-api";
import { useState } from "react";

export default function TasksPage() {
  const { data: tasks, loading, error, refresh } = useApi<any[]>("/api/tasks", []);
  const [message, setMessage] = useState("Summarize current platform status");
  const [status, setStatus] = useState("");

  async function createTask() {
    try {
      const result = await apiPost<{ task_id: string }>("/api/tasks", { message });
      setStatus(`Created ${result.task_id}`);
      await refresh();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : String(err));
    }
  }

  async function action(taskId: string, name: "pause" | "resume" | "cancel" | "retry") {
    try {
      await apiPost(`/api/tasks/${taskId}/${name}`);
      setStatus(`${name} ${taskId}`);
      await refresh();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Task Manager</h1>
      {loading ? <LoadingCard label="Loading tasks" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Create task">
        <div className="flex flex-col gap-3 lg:flex-row">
          <input value={message} onChange={(event) => setMessage(event.target.value)} className="h-11 flex-1 rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          <button onClick={createTask} className="h-11 rounded-full bg-[#2D8CFF] px-5 text-sm font-black text-white">Create</button>
        </div>
        <div className="mt-2 text-sm font-bold text-[#8c96a6]">{status}</div>
      </Card>
      <Card title="Tasks">
        <div className="overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[#8c96a6]"><tr><th className="p-2">ID</th><th>Status</th><th>Subagents</th><th>Message</th><th>Actions</th></tr></thead>
            <tbody className="text-[#30343b]">{tasks.map((task) => (
              <tr key={task.id} className="border-t border-[#e4e9f0]">
                <td className="p-2">{task.id}</td>
                <td>{task.status}</td>
                <td>{task.assigned_subagents?.length || 0}</td>
                <td>{task.message}</td>
                <td className="min-w-[260px] py-2">
                  <div className="flex flex-wrap gap-1">
                    {(["pause", "resume", "cancel", "retry"] as const).map((name) => (
                      <button key={name} onClick={() => action(task.id, name)} className="rounded-full bg-[#f6f8fb] px-3 py-1 text-xs font-black text-[#667085] hover:bg-[#eaf4ff] hover:text-[#2D8CFF]">{name}</button>
                    ))}
                  </div>
                </td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
