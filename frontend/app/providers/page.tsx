"use client";

import { Card, Pill } from "@/components/card";
import { ConfigControlCard } from "@/components/feature-controls";
import { LoadingCard } from "@/components/loading-card";
import { apiPost } from "@/lib/api";
import { useApi } from "@/lib/use-api";
import { useState } from "react";

type ProviderStatus = {
  name: string;
  config_path?: string;
  provider_type?: string;
  enabled: boolean;
  active: boolean;
  healthy: boolean;
  default_model?: string;
  base_url?: string;
  api_key_env?: string;
};

export default function ProvidersPage() {
  const { data: providers, loading, error, refresh } = useApi<ProviderStatus[]>("/api/providers/status", []);
  const [testMessage, setTestMessage] = useState("health check");
  const [testResult, setTestResult] = useState<Record<string, unknown> | null>(null);
  const [testStatus, setTestStatus] = useState("");

  async function testProvider(provider?: string) {
    try {
      const result = await apiPost<Record<string, unknown>>("/api/providers/test", { provider, message: testMessage });
      setTestResult(result);
      setTestStatus(provider ? `Tested ${provider}` : "Tested fallback chain");
    } catch (err) {
      setTestStatus(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Provider Manager</h1>
      {loading ? <LoadingCard label="Loading providers" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Providers">
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <input value={testMessage} onChange={(event) => setTestMessage(event.target.value)} className="h-11 min-w-[240px] rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          <button onClick={() => testProvider()} className="h-11 rounded-full bg-[#ffc247] px-4 text-sm font-black text-white">Test fallback</button>
          <span className="text-sm font-bold text-[#8c96a6]">{testStatus}</span>
        </div>
        <div className="grid gap-3 lg:grid-cols-2">
          {providers.map((provider) => (
            <div key={provider.name} className="space-y-2">
              <ConfigControlCard
                title={provider.name}
                subtitle={`${provider.provider_type || provider.name} provider`}
                status={provider.healthy ? "healthy" : provider.enabled ? "configured" : "disabled"}
                configPath={provider.config_path}
                initialConfig={{
                  version: 1,
                  name: provider.name,
                  provider_type: provider.provider_type || provider.name,
                  enabled: provider.enabled,
                  base_url: provider.base_url || "",
                  default_model: provider.default_model || "",
                  api_key_env: provider.api_key_env || ""
                }}
                fields={[
                  { key: "base_url", label: "Base URL" },
                  { key: "default_model", label: "Default model" },
                  { key: "api_key_env", label: "API key env" }
                ]}
                onReload={refresh}
              />
              <button onClick={() => testProvider(provider.name)} disabled={!provider.active} className="h-10 rounded-full bg-[#2D8CFF] px-4 text-xs font-black text-white disabled:bg-[#d6dde7]">Test this provider</button>
            </div>
          ))}
          {providers.length === 0 ? <Pill>No providers configured</Pill> : null}
        </div>
        {testResult ? <pre className="mt-4 overflow-auto rounded-[22px] bg-[#f6f8fb] p-4 text-sm font-bold text-[#667085]">{JSON.stringify(testResult, null, 2)}</pre> : null}
      </Card>
    </div>
  );
}
