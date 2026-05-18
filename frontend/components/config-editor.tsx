"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, RefreshCw, Save } from "lucide-react";
import { apiGet, apiPost, apiPut } from "@/lib/api";

type ValidationResult = { ok: boolean; errors?: string[]; path?: string };

export function ConfigEditor({ files }: { files: string[] }) {
  const [selected, setSelected] = useState(files[0] || "");
  const [content, setContent] = useState("{}");
  const [status, setStatus] = useState("Select a config file to edit.");
  const [busy, setBusy] = useState(false);
  const sortedFiles = useMemo(() => [...files].sort(), [files]);

  useEffect(() => {
    if (!selected) return;
    setBusy(true);
    apiGet<Record<string, unknown>>(`/api/config/${selected}`)
      .then((data) => {
        setContent(JSON.stringify(data, null, 2));
        setStatus(`Loaded ${selected}`);
      })
      .catch((error) => setStatus(String(error)))
      .finally(() => setBusy(false));
  }, [selected]);

  async function save() {
    setBusy(true);
    try {
      const parsed = JSON.parse(content);
      await apiPut(`/api/config/${selected}`, { data: parsed });
      const validation = await apiPost<ValidationResult>("/api/config/validate", { path: selected });
      setStatus(validation.ok ? `Saved and validated ${selected}` : `Saved, validation failed: ${(validation.errors || []).join("; ")}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  async function reload() {
    setBusy(true);
    try {
      const result = await apiPost<{ ok: boolean; reload_count?: number }>("/api/config/reload");
      setStatus(result.ok ? `Config reloaded (${result.reload_count ?? 0})` : "Reload failed. Check validation output.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[320px_1fr]">
      <div className="space-y-2">
        {sortedFiles.map((file) => (
          <button
            key={file}
            onClick={() => setSelected(file)}
            className={`w-full rounded-[18px] border p-3 text-left text-sm font-black transition ${selected === file ? "border-[#2D8CFF] bg-[#eaf4ff] text-[#2D8CFF]" : "border-[#e4e9f0] bg-white text-[#667085] hover:bg-[#f6f8fb]"}`}
          >
            {file}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          spellCheck={false}
          className="soft-shadow h-[520px] w-full resize-y rounded-[24px] border border-[#e4e9f0] bg-white p-4 font-mono text-sm text-[#30343b] outline-none focus:border-[#2D8CFF]"
        />
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#e4e9f0] bg-[#f6f8fb] px-4 py-2 text-sm font-bold text-[#667085]">
            <CheckCircle2 size={16} />
            {status}
          </div>
          <div className="flex gap-2">
            <button onClick={save} disabled={busy || !selected} className="inline-flex h-11 items-center gap-2 rounded-full bg-[#2D8CFF] px-4 text-sm font-black text-white disabled:opacity-50">
              <Save size={16} />
              Save
            </button>
            <button onClick={reload} disabled={busy} className="inline-flex h-11 items-center gap-2 rounded-full bg-[#ffc247] px-4 text-sm font-black text-white disabled:opacity-50">
              <RefreshCw size={16} />
              Reload
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
