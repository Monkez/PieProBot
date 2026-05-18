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
        <p className="text-sm text-slate-400">Submit work to the orchestrator while subagents handle execution.</p>
      </div>
      <textarea className="h-36 w-full rounded-md border border-line bg-slate-950 p-3 text-sm outline-none focus:border-accent" value={message} onChange={(event) => setMessage(event.target.value)} />
      <button onClick={submit} disabled={busy} className="inline-flex h-10 items-center gap-2 rounded-md bg-accent px-4 text-sm font-medium text-slate-950 disabled:opacity-60">
        <Send size={16} />
        {busy ? "Running" : "Send"}
      </button>
      {result && (
        <pre className="overflow-auto rounded-md border border-line bg-slate-950 p-4 text-sm text-slate-200">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}

