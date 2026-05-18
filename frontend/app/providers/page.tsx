import { Card } from "@/components/card";
import { Pill } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function ProvidersPage() {
  const providers = await apiGet<any[]>("/api/providers/status").catch(() => []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Provider Manager</h1>
      <Card title="Providers">
        <div className="grid gap-3 lg:grid-cols-2">
          {providers.map((provider) => (
            <div key={provider.name} className="rounded-[22px] border border-[#e4e9f0] bg-white p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-lg font-black text-[#30343b]">{provider.name}</div>
                  <div className="text-sm font-bold text-[#8c96a6]">{provider.provider_type || provider.name}</div>
                </div>
                <Pill>{provider.healthy ? "healthy" : provider.enabled ? "configured" : "disabled"}</Pill>
              </div>
              <div className="mt-3 space-y-1 text-sm font-bold text-[#667085]">
                <div>model: {provider.default_model || "not set"}</div>
                {provider.base_url ? <div className="break-all">base_url: {provider.base_url}</div> : null}
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
