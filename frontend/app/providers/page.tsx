"use client";

import { Card, Pill } from "@/components/card";
import { ConfigControlCard } from "@/components/feature-controls";
import { LoadingCard } from "@/components/loading-card";
import { apiPost, apiPut } from "@/lib/api";
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
  model_profiles?: {
    fast?: string;
    normal?: string;
    power?: string;
  };
  base_url?: string;
  api_key_env?: string;
};

type ProviderDraft = {
  name: string;
  provider_type: string;
  enabled: boolean;
  base_url: string;
  api_key_env: string;
  default_model: string;
  fast_model: string;
  normal_model: string;
  power_model: string;
};

const emptyDraft: ProviderDraft = {
  name: "",
  provider_type: "custom",
  enabled: true,
  base_url: "http://127.0.0.1:8080/v1",
  api_key_env: "CUSTOM_PROVIDER_API_KEY",
  default_model: "",
  fast_model: "",
  normal_model: "",
  power_model: ""
};

export default function ProvidersPage() {
  const { data: providers, loading, error, refresh } = useApi<ProviderStatus[]>("/api/providers/status", []);
  const [testMessage, setTestMessage] = useState("health check");
  const [testRoute, setTestRoute] = useState("normal");
  const [testResult, setTestResult] = useState<Record<string, unknown> | null>(null);
  const [testStatus, setTestStatus] = useState("");
  const [draft, setDraft] = useState<ProviderDraft>(emptyDraft);
  const [createStatus, setCreateStatus] = useState("");
  const [creating, setCreating] = useState(false);
  const canSubmit = Boolean(draft.name.trim() && draft.normal_model.trim());

  async function testProvider(provider?: string) {
    try {
      const result = await apiPost<Record<string, unknown>>("/api/providers/test", { provider, message: testMessage, route: testRoute });
      setTestResult(result);
      setTestStatus(provider ? `Tested ${provider} (${testRoute})` : `Tested fallback chain (${testRoute})`);
    } catch (err) {
      setTestStatus(err instanceof Error ? err.message : String(err));
    }
  }

  async function createProvider() {
    if (!canSubmit) {
      setCreateStatus("Name and normal model are required");
      return;
    }
    setCreating(true);
    setCreateStatus("Creating provider...");
    try {
      const sanitized = { ...draft, name: draft.name.trim().toLowerCase().replace(/[^a-z0-9_-]+/g, "-").replace(/^[-_]+|[-_]+$/g, "") };
      const result = await apiPost<{ path?: string }>("/api/providers", sanitized);
      setCreateStatus(`Created ${sanitized.name} in ${result.path || "config/providers"}`);
      setDraft(emptyDraft);
      await refresh();
    } catch (err) {
      setCreateStatus(err instanceof Error ? err.message : String(err));
    } finally {
      setCreating(false);
    }
  }

  function updateDraft(key: keyof ProviderDraft, value: string | boolean) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Provider Manager</h1>
      {loading ? <LoadingCard label="Loading providers" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="New Provider">
        <div className="grid gap-3 lg:grid-cols-4">
          <label className="block">
            <span className="text-xs font-black uppercase text-[#9aa3af]">Name</span>
            <input value={draft.name} onChange={(event) => updateDraft("name", event.target.value)} placeholder="deepseek" className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          </label>
          <label className="block">
            <span className="text-xs font-black uppercase text-[#9aa3af]">Type</span>
            <select value={draft.provider_type} onChange={(event) => updateDraft("provider_type", event.target.value)} className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]">
              <option value="custom">Custom</option>
              <option value="openai_compatible">OpenAI compatible</option>
              <option value="openai">OpenAI</option>
              <option value="local">Local</option>
            </select>
          </label>
          <label className="block lg:col-span-2">
            <span className="text-xs font-black uppercase text-[#9aa3af]">Base URL</span>
            <input value={draft.base_url} onChange={(event) => updateDraft("base_url", event.target.value)} className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          </label>
          <label className="block">
            <span className="text-xs font-black uppercase text-[#9aa3af]">API key or env</span>
            <input value={draft.api_key_env} onChange={(event) => updateDraft("api_key_env", event.target.value)} className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          </label>
          <label className="block">
            <span className="text-xs font-black uppercase text-[#9aa3af]">Fast model</span>
            <input value={draft.fast_model} onChange={(event) => updateDraft("fast_model", event.target.value)} className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          </label>
          <label className="block">
            <span className="text-xs font-black uppercase text-[#9aa3af]">Normal model</span>
            <input value={draft.normal_model} onChange={(event) => updateDraft("normal_model", event.target.value)} className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          </label>
          <label className="block">
            <span className="text-xs font-black uppercase text-[#9aa3af]">Power model</span>
            <input value={draft.power_model} onChange={(event) => updateDraft("power_model", event.target.value)} className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          </label>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button
            onClick={createProvider}
            disabled={creating}
            className="h-10 rounded-full bg-[#2D8CFF] px-4 text-sm font-black text-white shadow-sm transition hover:bg-[#1677e8] disabled:bg-[#8c96a6]"
          >
            {creating ? "Creating..." : "Create provider"}
          </button>
          <span className={`rounded-full px-3 py-2 text-sm font-bold ${createStatus.includes("Created") ? "bg-[#e8f8f2] text-[#198f68]" : createStatus ? "bg-[#fff0ea] text-[#c7512f]" : "text-[#8c96a6]"}`}>
            {createStatus || (canSubmit ? "Ready to create" : "Name and normal model are required")}
          </span>
        </div>
      </Card>
      <Card title="Providers">
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <input value={testMessage} onChange={(event) => setTestMessage(event.target.value)} className="h-11 min-w-[240px] rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          <select value={testRoute} onChange={(event) => setTestRoute(event.target.value)} className="h-11 rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]">
            <option value="fast">Fast</option>
            <option value="normal">Normal</option>
            <option value="power">Power</option>
          </select>
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
                  model_profiles: provider.model_profiles || {
                    fast: provider.default_model || "",
                    normal: provider.default_model || "",
                    power: provider.default_model || ""
                  },
                  api_key_env: provider.api_key_env || ""
                }}
                fields={[
                  { key: "base_url", label: "Base URL" },
                  { key: "default_model", label: "Default model" },
                  { key: "model_profiles.fast", label: "Fast model" },
                  { key: "model_profiles.normal", label: "Normal model" },
                  { key: "model_profiles.power", label: "Power model" },
                  { key: "api_key_env", label: "API key env" }
                ]}
                onSave={async (config) => {
                  await apiPut(`/api/providers/${provider.name}`, config);
                }}
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
