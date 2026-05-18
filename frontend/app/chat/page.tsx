"use client";

import { useState } from "react";
import { Send } from "lucide-react";
import { apiPost } from "@/lib/api";

type ChatResult = { task_id: string; status: string; response: string };

export default function ChatPage() {
  const [message, setMessage] = useState("Summarize current platform status");
  const [result, setResult] = useState<ChatResult | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true);
    try {
      setResult(await apiPost<ChatResult>("/api/chat/wait", { message }));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-black text-[#30343b]">Chat Console</h1>
        <p className="text-sm font-bold text-[#8c96a6]">Submit work to the orchestrator while subagents handle execution.</p>
      </div>
      <textarea className="soft-shadow h-36 w-full rounded-[24px] border border-[#e4e9f0] bg-white p-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" value={message} onChange={(event) => setMessage(event.target.value)} />
      <button onClick={submit} disabled={busy} className="inline-flex h-12 items-center gap-2 rounded-full bg-[#2D8CFF] px-5 text-sm font-black text-white shadow-[0_12px_24px_rgba(45,140,255,0.22)] disabled:opacity-60">
        <Send size={16} />
        {busy ? "Running" : "Send"}
      </button>
      {result && (
        <pre className="soft-shadow overflow-auto rounded-[24px] border border-[#e4e9f0] bg-white p-4 text-sm font-bold text-[#667085]">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
