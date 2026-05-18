"use client";

import { useMemo, useState } from "react";
import { Send } from "lucide-react";
import { apiPost } from "@/lib/api";

type ChannelStatus = {
  name: string;
  type: string;
  enabled: boolean;
  active: boolean;
  healthy: boolean;
  default_chat_id_configured?: boolean;
};

export function ChannelConsole({ channels }: { channels: ChannelStatus[] }) {
  const first = channels[0]?.name || "telegram";
  const [channel, setChannel] = useState(first);
  const [recipient, setRecipient] = useState("");
  const [text, setText] = useState("PiePro test message");
  const [status, setStatus] = useState("Configure Telegram in config/channels/telegram.yaml, then reload config.");
  const active = useMemo(() => channels.find((item) => item.name === channel), [channels, channel]);

  async function send() {
    try {
      const result = await apiPost<{ ok: boolean; error?: string; message_id?: string }>(`/api/channels/${channel}/send`, {
        recipient: recipient || undefined,
        text
      });
      setStatus(result.ok ? `Sent via ${channel}${result.message_id ? ` (#${result.message_id})` : ""}` : `Send failed: ${result.error}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : String(error));
    }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_1.2fr]">
      <div className="space-y-3">
        {channels.map((item) => (
          <button
            key={item.name}
            onClick={() => setChannel(item.name)}
            className={`w-full rounded-[22px] border p-4 text-left transition ${channel === item.name ? "border-[#2D8CFF] bg-[#eaf4ff]" : "border-[#e4e9f0] bg-white hover:bg-[#f6f8fb]"}`}
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-lg font-black text-[#30343b]">{item.name}</div>
                <div className="text-sm font-bold text-[#8c96a6]">{item.type}</div>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs font-black ${item.healthy ? "bg-[#e8f8f2] text-[#23a77b]" : "bg-[#fff4d9] text-[#b77a00]"}`}>
                {item.healthy ? "healthy" : item.enabled ? "needs token" : "disabled"}
              </span>
            </div>
          </button>
        ))}
      </div>
      <div className="space-y-3 rounded-[24px] border border-[#e4e9f0] bg-[#f6f8fb] p-4">
        <div>
          <div className="text-xl font-black text-[#30343b]">Send message</div>
          <div className="text-sm font-bold text-[#8c96a6]">
            {active?.default_chat_id_configured ? "Default recipient is configured." : "Telegram requires a chat_id recipient unless default_chat_id is set."}
          </div>
        </div>
        <input value={recipient} onChange={(event) => setRecipient(event.target.value)} placeholder="Telegram chat_id or channel recipient" className="h-12 w-full rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
        <textarea value={text} onChange={(event) => setText(event.target.value)} className="h-32 w-full rounded-[22px] border border-[#e4e9f0] bg-white p-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="text-sm font-bold text-[#667085]">{status}</div>
          <button onClick={send} className="inline-flex h-11 items-center gap-2 rounded-full bg-[#2D8CFF] px-4 text-sm font-black text-white">
            <Send size={16} />
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
