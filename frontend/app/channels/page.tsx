import { Card } from "@/components/card";
import { ChannelConsole } from "@/components/channel-console";
import { apiGet } from "@/lib/api";

type ChannelStatus = {
  name: string;
  type: string;
  enabled: boolean;
  active: boolean;
  healthy: boolean;
};

export default async function ChannelsPage() {
  const channels = await apiGet<ChannelStatus[]>("/api/channels").catch(() => []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Channels</h1>
      <Card title="Messaging channels">
        <ChannelConsole channels={channels.length ? channels : [{ name: "telegram", type: "telegram", enabled: false, active: false, healthy: false }]} />
      </Card>
    </div>
  );
}
