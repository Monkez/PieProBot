import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function SelfUpdatePage() {
  const status = await apiGet<any>("/api/self-update/status").catch(() => ({ candidates: [], history: [] }));
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Self-Update Center</h1>
      <Card title="Stable and candidates">
        <pre className="overflow-auto text-sm">{JSON.stringify(status, null, 2)}</pre>
      </Card>
    </div>
  );
}

