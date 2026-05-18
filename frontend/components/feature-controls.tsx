"use client";

import { useState } from "react";
import { RefreshCw, Save } from "lucide-react";
import { apiGet, apiPost, apiPut } from "@/lib/api";

type ConfigData = Record<string, any>;

export function ToggleField({ checked, onChange }: { checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={`h-7 w-12 rounded-full p-1 transition ${checked ? "bg-[#2D8CFF]" : "bg-[#d6dde7]"}`}
      aria-label={checked ? "Enabled" : "Disabled"}
    >
      <span className={`block h-5 w-5 rounded-full bg-white transition ${checked ? "translate-x-5" : "translate-x-0"}`} />
    </button>
  );
}

export function ConfigControlCard({
  title,
  subtitle,
  status,
  configPath,
  fields,
  reloadLabel = "Reload config",
  onReload,
  initialConfig
}: {
  title: string;
  subtitle: string;
  status: string;
  configPath?: string;
  fields: Array<{ key: string; label: string; kind?: "text" | "number" | "boolean" }>;
  reloadLabel?: string;
  onReload?: () => Promise<void>;
  initialConfig?: ConfigData;
}) {
  const [config, setConfig] = useState<ConfigData | null>(initialConfig || null);
  const [message, setMessage] = useState(status);
  const [busy, setBusy] = useState(false);

  async function load() {
    if (!configPath) return;
    setBusy(true);
    try {
      setConfig(await apiGet<ConfigData>(`/api/config/${configPath}`));
      setMessage(`Loaded ${configPath}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  async function save() {
    if (!configPath || !config) return;
    setBusy(true);
    try {
      await apiPut(`/api/config/${configPath}`, { data: config });
      await apiPost("/api/config/reload");
      await onReload?.();
      setMessage(`Saved ${configPath}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  const editable = config || {};

  return (
    <div className="rounded-[22px] border border-[#e4e9f0] bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-lg font-black text-[#30343b]">{title}</div>
          <div className="text-sm font-bold text-[#8c96a6]">{subtitle}</div>
        </div>
        {configPath ? <ToggleField checked={Boolean(editable.enabled ?? false)} onChange={(value) => setConfig({ ...editable, enabled: value })} /> : null}
      </div>
      <div className="mt-3 space-y-2">
        {fields.map((field) => (
          <label key={field.key} className="block">
            <span className="text-xs font-black uppercase text-[#9aa3af]">{field.label}</span>
            {field.kind === "boolean" ? (
              <div className="mt-1"><ToggleField checked={Boolean(editable[field.key])} onChange={(value) => setConfig({ ...editable, [field.key]: value })} /></div>
            ) : (
              <input
                type={field.kind === "number" ? "number" : "text"}
                value={editable[field.key] ?? ""}
                onChange={(event) => setConfig({ ...editable, [field.key]: field.kind === "number" ? Number(event.target.value) : event.target.value })}
                className="mt-1 h-10 w-full rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-3 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]"
              />
            )}
          </label>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
        <div className="text-xs font-bold text-[#8c96a6]">{message}</div>
        <div className="flex gap-2">
          <button onClick={load} disabled={!configPath || busy} className="inline-flex h-9 items-center gap-1 rounded-full bg-[#f6f8fb] px-3 text-xs font-black text-[#667085] disabled:opacity-50">
            <RefreshCw size={14} />
            Load
          </button>
          <button onClick={save} disabled={!configPath || busy || !config} className="inline-flex h-9 items-center gap-1 rounded-full bg-[#2D8CFF] px-3 text-xs font-black text-white disabled:opacity-50">
            <Save size={14} />
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
