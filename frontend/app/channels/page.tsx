"use client";

import { Card } from "@/components/card";
import { ChannelConsole } from "@/components/channel-console";
import { ConfigControlCard } from "@/components/feature-controls";
import { LoadingCard } from "@/components/loading-card";
import { useApi } from "@/lib/use-api";

type ChannelStatus = {
  name: string;
  config_path?: string;
  type: string;
  enabled: boolean;
  active: boolean;
  healthy: boolean;
  bot_token_env?: string;
  default_chat_id?: string;
  api_base?: string;
  timeout_seconds?: number;
  default_chat_id_configured?: boolean;
};

const fallback: ChannelStatus[] = [{ name: "telegram", type: "telegram", enabled: false, active: false, healthy: false }];

export default function ChannelsPage() {
  const { data, loading, error, refresh } = useApi<ChannelStatus[]>("/api/channels", []);
  const channels = data.length ? data : fallback;
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Channels</h1>
      {loading ? <LoadingCard label="Loading channels" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Channel settings">
        <div className="grid gap-3 lg:grid-cols-2">
          {channels.map((channel) => (
            <ConfigControlCard
              key={channel.name}
              title={channel.name}
              subtitle={`${channel.type} channel`}
              status={channel.healthy ? "healthy" : channel.enabled ? "needs token or recipient" : "disabled"}
              configPath={channel.config_path}
              initialConfig={{
                version: 1,
                name: channel.name,
                type: channel.type,
                enabled: channel.enabled,
                bot_token_env: channel.bot_token_env || "TELEGRAM_BOT_TOKEN",
                default_chat_id: channel.default_chat_id || "",
                api_base: channel.api_base || "https://api.telegram.org",
                timeout_seconds: channel.timeout_seconds ?? 10
              }}
              fields={[
                { key: "bot_token_env", label: "Token env" },
                { key: "default_chat_id", label: "Default chat id" },
                { key: "api_base", label: "API base" },
                { key: "timeout_seconds", label: "Timeout seconds", kind: "number" }
              ]}
              onReload={refresh}
            />
          ))}
        </div>
      </Card>
      <Card title="Messaging channels">
        <ChannelConsole channels={channels} />
      </Card>
    </div>
  );
}
