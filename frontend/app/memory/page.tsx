import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function MemoryPage() {
  const [items, status] = await Promise.all([
    apiGet<any[]>("/api/memory/search?q=").catch(() => []),
    apiGet<any>("/api/memory/status").catch(() => ({ external_enabled: false }))
  ]);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Memory Explorer</h1>
      <Card title="Backend status">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(status, null, 2)}</pre>
      </Card>
      <Card title="Memory items">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(items, null, 2)}</pre>
      </Card>
    </div>
  );
}
