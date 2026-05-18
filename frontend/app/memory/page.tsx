"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { apiGet } from "@/lib/api";

export default function MemoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState<any>({ external_enabled: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiGet<any[]>("/api/memory/search?q=").catch(() => []),
      apiGet<any>("/api/memory/status").catch(() => ({ external_enabled: false }))
    ])
      .then(([nextItems, nextStatus]) => {
        setItems(nextItems);
        setStatus(nextStatus);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Memory Explorer</h1>
      {loading ? <LoadingCard label="Loading memory" /> : null}
      <Card title="Backend status">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(status, null, 2)}</pre>
      </Card>
      <Card title="Memory items">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(items, null, 2)}</pre>
      </Card>
    </div>
  );
}
