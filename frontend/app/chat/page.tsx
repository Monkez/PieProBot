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
        <h1 className="text-2xl font-semibold">Chat Console</h1>
        <p className="text-sm font-bold text-black/50">Submit work to the orchestrator while subagents handle execution.</p>
      </div>
      <textarea className="soft-shadow h-36 w-full rounded-[24px] border border-black/10 bg-white/80 p-4 text-sm font-bold text-black outline-none focus:border-black" value={message} onChange={(event) => setMessage(event.target.value)} />
      <button onClick={submit} disabled={busy} className="inline-flex h-12 items-center gap-2 rounded-full bg-black px-5 text-sm font-black text-white disabled:opacity-60">
        <Send size={16} />
        {busy ? "Running" : "Send"}
      </button>
      {result && (
        <pre className="soft-shadow overflow-auto rounded-[24px] border border-black/10 bg-white/80 p-4 text-sm font-bold text-black/70">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}
