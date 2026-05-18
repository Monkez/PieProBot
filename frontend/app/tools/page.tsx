"use client";

import { Card } from "@/components/card";
import { ConfigControlCard } from "@/components/feature-controls";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

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
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Tool Registry</h1>
      {loading ? <LoadingCard label="Loading tools" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Tools">
        <div className="grid gap-3 lg:grid-cols-2">
          {tools.map((tool) => (
            <ConfigControlCard
              key={tool.name}
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
          ))}
        </div>
      </Card>
    </div>
  );
}
