"use client";

import { Card } from "@/components/card";
import { ConfigControlCard } from "@/components/feature-controls";
import { LoadingCard } from "@/components/loading-card";
import { apiPost } from "@/lib/api";
import { useApi } from "@/lib/use-api";
import { useState } from "react";

type ToolStatus = {
  name: string;
  version: string | number;
  description: string;
  category: string;
  enabled: boolean;
  timeout_seconds: number;
  audit_level: string;
  permissions: Record<string, boolean>;
  input_schema: Record<string, unknown>;
  output_schema: Record<string, unknown>;
  retry_policy: Record<string, unknown>;
  sandbox_policy: Record<string, unknown>;
  rate_limit: Record<string, unknown>;
  handler?: string;
  config_path?: string;
};

export default function ToolsPage() {
  const { data: tools, loading, error, refresh } = useApi<ToolStatus[]>("/api/tools", []);
  const [payloads, setPayloads] = useState<Record<string, string>>({});
  const [result, setResult] = useState<Record<string, unknown> | null>(null);

  async function executeTool(name: string) {
    try {
      const payload = JSON.parse(payloads[name] || "{}");
      const response = await apiPost<Record<string, unknown>>(`/api/tools/${name}/execute`, {
        payload,
        permissions: { network: true, filesystem: true, memory: true, shell: false }
      });
      setResult({ tool: name, ...response });
    } catch (err) {
      setResult({ tool: name, ok: false, error: err instanceof Error ? err.message : String(err) });
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Tool Registry</h1>
      {loading ? <LoadingCard label="Loading tools" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Tools">
        <div className="grid gap-3 lg:grid-cols-2">
          {tools.map((tool) => (
            <div key={tool.name} className="space-y-2">
              <ConfigControlCard
                title={tool.name}
                subtitle={tool.description}
                status={`${tool.category} / ${tool.audit_level}`}
                configPath={tool.config_path}
                initialConfig={{
                  version: tool.version,
                  name: tool.name,
                  description: tool.description,
                  category: tool.category,
                  enabled: tool.enabled,
                  input_schema: tool.input_schema,
                  output_schema: tool.output_schema,
                  permissions: tool.permissions,
                  timeout_seconds: tool.timeout_seconds,
                  retry_policy: tool.retry_policy,
                  sandbox_policy: tool.sandbox_policy,
                  rate_limit: tool.rate_limit,
                  audit_level: tool.audit_level,
                  handler: tool.handler
                }}
                fields={[
                  { key: "description", label: "Description" },
                  { key: "category", label: "Category" },
                  { key: "timeout_seconds", label: "Timeout seconds", kind: "number" },
                  { key: "audit_level", label: "Audit level" }
                ]}
                onReload={refresh}
              />
              <textarea
                value={payloads[tool.name] || "{}"}
                onChange={(event) => setPayloads({ ...payloads, [tool.name]: event.target.value })}
                className="h-24 w-full rounded-[18px] border border-[#e4e9f0] bg-white p-3 font-mono text-xs text-[#30343b] outline-none focus:border-[#2D8CFF]"
              />
              <button onClick={() => executeTool(tool.name)} disabled={!tool.enabled} className="h-10 rounded-full bg-[#2D8CFF] px-4 text-xs font-black text-white disabled:bg-[#d6dde7]">Execute test call</button>
            </div>
          ))}
        </div>
        {result ? <pre className="mt-4 overflow-auto rounded-[22px] bg-[#f6f8fb] p-4 text-sm font-bold text-[#667085]">{JSON.stringify(result, null, 2)}</pre> : null}
      </Card>
    </div>
  );
}
