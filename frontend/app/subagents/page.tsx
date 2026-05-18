"use client";

import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

export default function SubagentsPage() {
  const { data: subagents, loading, error } = useApi<any[]>("/api/subagents", []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Subagent Monitor</h1>
      {loading ? <LoadingCard label="Loading subagents" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Active and historical subagents">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(subagents, null, 2)}</pre>
      </Card>
    </div>
  );
}
