import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function ProvidersPage() {
  const providers = await apiGet<any[]>("/api/providers/status").catch(() => []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Provider Manager</h1>
      <Card title="Providers">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(providers, null, 2)}</pre>
      </Card>
    </div>
  );
}
