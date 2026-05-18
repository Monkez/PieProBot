"use client";

import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

export default function LogsPage() {
  const { data: logs, loading, error } = useApi<any>("/logs", { logs: [] });
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Logs & Observability</h1>
      {loading ? <LoadingCard label="Loading logs" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Structured logs">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(logs, null, 2)}</pre>
      </Card>
    </div>
  );
}
