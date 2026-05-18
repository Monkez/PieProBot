"use client";

import { Card, Pill } from "@/components/card";
import { ConfigControlCard } from "@/components/feature-controls";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

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
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Provider Manager</h1>
      {loading ? <LoadingCard label="Loading providers" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Providers">
        <div className="grid gap-3 lg:grid-cols-2">
          {providers.map((provider) => (
            <ConfigControlCard
              key={provider.name}
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
          ))}
          {providers.length === 0 ? <Pill>No providers configured</Pill> : null}
        </div>
      </Card>
    </div>
  );
}
