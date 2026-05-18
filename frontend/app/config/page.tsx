"use client";

import { Card } from "@/components/card";
import { ConfigEditor } from "@/components/config-editor";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

export default function ConfigPage() {
  const { data: config, loading, error } = useApi<{ files: string[] }>("/api/config", { files: [] });
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Config Editor</h1>
      {loading ? <LoadingCard label="Loading config files" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Editable runtime config">
        <ConfigEditor files={config.files} />
      </Card>
    </div>
  );
}
