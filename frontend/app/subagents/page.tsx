"use client";

import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { apiPost } from "@/lib/api";
import { useApi } from "@/lib/use-api";
import { useState } from "react";

export default function SubagentsPage() {
  const { data: subagents, loading, error, refresh } = useApi<any[]>("/api/subagents", []);
  const [status, setStatus] = useState("");

  async function kill(id: string) {
    try {
      await apiPost(`/api/subagents/${id}/kill`);
      setStatus(`Killed ${id}`);
      await refresh();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Subagent Monitor</h1>
      {loading ? <LoadingCard label="Loading subagents" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      {status ? <div className="rounded-[22px] bg-[#eaf4ff] p-4 text-sm font-bold text-[#2D8CFF]">{status}</div> : null}
      <Card title="Active and historical subagents">
        <div className="grid gap-3 lg:grid-cols-2">
          {subagents.map((agent) => (
            <div key={agent.id} className="rounded-[22px] border border-[#e4e9f0] bg-white p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-lg font-black text-[#30343b]">{agent.type}</div>
                  <div className="text-sm font-bold text-[#8c96a6]">{agent.id}</div>
                </div>
                <span className="rounded-full bg-[#f6f8fb] px-3 py-1 text-xs font-black text-[#667085]">{agent.status}</span>
              </div>
              <div className="mt-3 text-sm font-bold text-[#667085]">task: {agent.task_id}</div>
              <div className="mt-1 text-sm font-bold text-[#667085]">step: {agent.current_step}</div>
              <button onClick={() => kill(agent.id)} disabled={["completed", "failed", "cancelled", "destroyed"].includes(agent.status)} className="mt-4 h-10 rounded-full bg-[#ff8a61] px-4 text-xs font-black text-white disabled:bg-[#d6dde7]">Kill</button>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
