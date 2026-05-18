import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function ToolsPage() {
  const tools = await apiGet<any[]>("/api/tools").catch(() => []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Tool Registry</h1>
      <div className="grid gap-3 lg:grid-cols-2">
        {tools.map((tool) => (
          <Card key={tool.name} title={tool.name}>
            <div className="text-sm font-bold text-[#667085]">{tool.description}</div>
            <div className="mt-3 text-xs font-black text-[#9aa3af]">enabled={String(tool.enabled)} audit={tool.audit_level}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
