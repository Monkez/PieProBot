"use client";

import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

export default function SelfUpdatePage() {
  const { data: status, loading, error } = useApi<any>("/api/self-update/status", { candidates: [], history: [] });
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Self-Update Center</h1>
      {loading ? <LoadingCard label="Loading self-update status" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Stable and candidates">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(status, null, 2)}</pre>
      </Card>
    </div>
  );
}
