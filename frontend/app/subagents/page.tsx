import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function SubagentsPage() {
  const subagents = await apiGet<any[]>("/api/subagents").catch(() => []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Subagent Monitor</h1>
      <Card title="Active and historical subagents">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(subagents, null, 2)}</pre>
      </Card>
    </div>
  );
}
