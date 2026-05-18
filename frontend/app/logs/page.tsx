import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function LogsPage() {
  const logs = await apiGet<any>("/logs").catch(() => ({ logs: [] }));
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Logs & Observability</h1>
      <Card title="Structured logs">
        <pre className="overflow-auto text-sm">{JSON.stringify(logs, null, 2)}</pre>
      </Card>
    </div>
  );
}

