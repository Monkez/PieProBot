import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function SubagentsPage() {
  const subagents = await apiGet<any[]>("/api/subagents").catch(() => []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Subagent Monitor</h1>
      <Card title="Active and historical subagents">
        <pre className="overflow-auto text-sm">{JSON.stringify(subagents, null, 2)}</pre>
      </Card>
    </div>
  );
}

