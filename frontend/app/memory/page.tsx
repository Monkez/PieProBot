"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { apiDelete, apiGet, apiPost } from "@/lib/api";

export default function MemoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [status, setStatus] = useState<any>({ external_enabled: false });
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [content, setContent] = useState("");
  const [message, setMessage] = useState("");

  async function load(nextQuery = query) {
    setLoading(true);
    const [nextItems, nextStatus] = await Promise.all([
      apiGet<any[]>(`/api/memory/search?q=${encodeURIComponent(nextQuery)}`).catch(() => []),
      apiGet<any>("/api/memory/status").catch(() => ({ external_enabled: false }))
    ]);
    setItems(nextItems);
    setStatus(nextStatus);
    setLoading(false);
  }

  useEffect(() => {
    load("");
  }, []);

  async function saveMemory() {
    try {
      const item = await apiPost<any>("/api/memory", { content });
      setMessage(`Saved ${item.id}`);
      setContent("");
      await load(query);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  async function deleteMemory(id: string) {
    await apiDelete(`/api/memory/${id}`);
    setMessage(`Deleted ${id}`);
    await load(query);
  }

  async function compact() {
    const result = await apiPost<Record<string, unknown>>("/api/memory/compact");
    setMessage(`Compacted: ${JSON.stringify(result)}`);
    await load(query);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Memory Explorer</h1>
      {loading ? <LoadingCard label="Loading memory" /> : null}
      <Card title="Memory controls">
        <div className="grid gap-3 lg:grid-cols-[1fr_auto]">
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search memory" className="h-11 rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          <button onClick={() => load(query)} className="h-11 rounded-full bg-[#2D8CFF] px-5 text-sm font-black text-white">Search</button>
        </div>
        <div className="mt-3 grid gap-3 lg:grid-cols-[1fr_auto_auto]">
          <input value={content} onChange={(event) => setContent(event.target.value)} placeholder="New memory content" className="h-11 rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          <button onClick={saveMemory} disabled={!content.trim()} className="h-11 rounded-full bg-[#ffc247] px-5 text-sm font-black text-white disabled:bg-[#d6dde7]">Save</button>
          <button onClick={compact} className="h-11 rounded-full bg-[#f6f8fb] px-5 text-sm font-black text-[#667085]">Compact</button>
        </div>
        <div className="mt-2 text-sm font-bold text-[#8c96a6]">{message}</div>
      </Card>
      <Card title="Backend status">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(status, null, 2)}</pre>
      </Card>
      <Card title="Memory items">
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} className="rounded-[18px] border border-[#e4e9f0] bg-white p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="font-black text-[#30343b]">{item.type}</div>
                  <div className="text-sm font-bold text-[#667085]">{item.content}</div>
                  <div className="mt-1 text-xs font-bold text-[#9aa3af]">{item.id}</div>
                </div>
                <button onClick={() => deleteMemory(item.id)} className="rounded-full bg-[#fff0ea] px-3 py-1 text-xs font-black text-[#c7512f]">Delete</button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
