import { AvatarStack, Card, Pill, ProgressBar, Stat } from "@/components/card";
import { apiGet } from "@/lib/api";
import { Bot, Brain, CheckCircle2, Clock3, MessageCircle, Plus, Server, ShieldCheck, Sparkles } from "lucide-react";

async function load() {
  const [health, ready, metrics, tasks, subagents, tools, providers, memory, updates] = await Promise.all([
    apiGet<{ status: string; service?: string }>("/health").catch(() => ({ status: "offline" })),
    apiGet<{ tools: number }>("/ready").catch(() => ({ tools: 0 })),
    apiGet<Record<string, number>>("/metrics").catch(() => ({})),
    apiGet<any[]>("/api/tasks").catch(() => []),
    apiGet<any[]>("/api/subagents").catch(() => []),
    apiGet<any[]>("/api/tools").catch(() => []),
    apiGet<any[]>("/api/providers").catch(() => []),
    apiGet<{ external_enabled?: boolean; external_healthy?: boolean; local_items?: number }>("/api/memory/status").catch(() => ({ local_items: 0 })),
    apiGet<{ candidates?: unknown[]; history?: unknown[] }>("/api/self-update/status").catch(() => ({ candidates: [], history: [] }))
  ]);
  return { health, ready, metrics, tasks, subagents, tools, providers, memory, updates };
}

const statusTone = {
  completed: "bg-[#e8f8f2]",
  running: "bg-[#eaf4ff]",
  pending: "bg-[#fff4d9]",
  failed: "bg-[#fff0ea]",
  cancelled: "bg-[#f5f7fa]",
  paused: "bg-[#f5f7fa]"
};
const activityCards = [
  { name: "Runtime", message: "Backend and frontend are managed by piepro CLI.", Icon: CheckCircle2 },
  { name: "Docs", message: "Design system is now part of self-knowledge.", Icon: MessageCircle },
  { name: "Memory", message: "Memory mode is active.", Icon: Brain }
];

export default async function DashboardPage() {
  const data = await load();
  const memory = {
    external_enabled: false,
    external_healthy: false,
    local_items: 0,
    ...data.memory
  };
  const activeSubagents = data.subagents.filter((item) => ["running", "waiting_for_tool", "reporting"].includes(item.status)).length;
  const recentTasks = data.tasks.slice(-5).reverse();
  const enabledTools = data.tools.filter((tool) => tool.enabled).length;
  const activeProviders = data.providers.filter((provider) => provider.active).length;
  const memoryLabel = memory.external_enabled ? (memory.external_healthy ? "TencentDB healthy" : "Local fallback") : "Local";

  return (
    <div className="space-y-7">
      <section className="grid gap-4 xl:grid-cols-[1.1fr_1.9fr]">
        <Card title="Runtime Overview" className="min-h-[260px]">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="grid h-16 w-16 place-items-center rounded-full border-4 border-white bg-[#2D8CFF] text-2xl font-black text-white shadow-[0_14px_28px_rgba(45,140,255,0.24)]">P</div>
              <div>
                <div className="text-2xl font-black text-[#30343b]">PiePro</div>
                <div className="text-sm font-bold text-[#8c96a6]">Local agent runtime</div>
              </div>
            </div>
            <Pill dark>{data.health.status}</Pill>
          </div>
          <div className="mt-8 grid grid-cols-2 gap-3">
            <Pill>{memoryLabel}</Pill>
            <Pill>{enabledTools}/{data.tools.length} tools</Pill>
            <Pill>{activeProviders} active provider</Pill>
            <Pill>{data.updates.candidates?.length ?? 0} candidates</Pill>
          </div>
          <div className="mt-8 rounded-[22px] border border-[#e4e9f0] bg-[#f6f8fb] p-4">
            <div className="mb-2 flex items-center justify-between text-sm font-black text-[#30343b]">
              <span>System readiness</span>
              <span>{data.health.status === "ok" ? "100%" : "35%"}</span>
            </div>
            <ProgressBar value={data.health.status === "ok" ? 100 : 35} />
          </div>
        </Card>

        <Card title="Agent Control Center">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <Pill dark>Workspace pulse</Pill>
            <div className="flex gap-2">
              <button className="grid h-11 w-11 place-items-center rounded-full bg-white text-[#2D8CFF] soft-shadow" aria-label="Create task">
                <Plus size={18} />
              </button>
              <button className="grid h-11 w-11 place-items-center rounded-full bg-[#ffc247] text-white shadow-[0_12px_24px_rgba(255,194,71,0.24)]" aria-label="Smart action">
                <Sparkles size={18} />
              </button>
            </div>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-[24px] border border-[#e4e9f0] bg-[#fff4d9] p-5">
              <Server className="mb-5 text-[#ff9f1c]" size={24} />
              <div className="text-xl font-black text-[#30343b]">Backend</div>
              <div className="mt-1 text-sm font-bold text-[#8c96a6]">FastAPI orchestration runtime</div>
              <div className="mt-5"><ProgressBar value={data.health.status === "ok" ? 100 : 35} color="#ffc247" /></div>
            </div>
            <div className="rounded-[24px] border border-[#e4e9f0] bg-[#eaf4ff] p-5">
              <Bot className="mb-5 text-[#2D8CFF]" size={24} />
              <div className="text-xl font-black text-[#30343b]">Subagents</div>
              <div className="mt-1 text-sm font-bold text-[#8c96a6]">{activeSubagents} active workers</div>
              <div className="mt-5"><ProgressBar value={Math.min(activeSubagents * 20, 100)} /></div>
            </div>
            <div className="rounded-[24px] border border-[#e4e9f0] bg-[#fff0ea] p-5">
              <Brain className="mb-5 text-[#ff8a61]" size={24} />
              <div className="text-xl font-black text-[#30343b]">Memory</div>
              <div className="mt-1 text-sm font-bold text-[#8c96a6]">{memory.local_items ?? 0} local items</div>
              <div className="mt-5"><ProgressBar value={memory.external_healthy ? 100 : 55} color="#ff8a61" /></div>
            </div>
          </div>
        </Card>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <Stat label="Tasks" value={data.tasks.length} tone="yellow" />
        <Stat label="Subagents" value={data.subagents.length} tone="blue" />
        <Stat label="Tools" value={data.tools.length} tone="pink" />
        <Stat label="Providers" value={data.providers.length} tone="sage" />
        <Stat label="Updates" value={data.updates.history?.length ?? 0} tone="gray" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <Card title="Task Queue">
          <div className="space-y-3">
            {recentTasks.length === 0 ? (
              <div className="rounded-[24px] border border-[#e4e9f0] bg-[#f6f8fb] p-6 text-sm font-bold text-[#8c96a6]">No tasks yet. Send a message from Chat Console to create one.</div>
            ) : (
              recentTasks.map((task) => (
                <div key={task.id} className={`rounded-[24px] border border-[#e4e9f0] p-4 ${statusTone[task.status as keyof typeof statusTone] ?? "bg-white/80"}`}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="text-lg font-black">{task.message}</div>
                      <div className="mt-1 text-xs font-black text-[#9aa3af]">{task.id}</div>
                    </div>
                    <Pill>{task.status}</Pill>
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <AvatarStack names={(task.assigned_subagents ?? []).length ? task.assigned_subagents : ["P"]} />
                    <div className="text-sm font-black text-[#8c96a6]">{task.assigned_subagents?.length ?? 0} subagents</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        <Card title="Provider & Tool Health">
          <div className="space-y-3">
            {data.providers.map((provider) => (
              <div key={provider.name} className={`flex items-center justify-between rounded-[22px] border border-[#e4e9f0] p-4 ${provider.active ? "bg-[#e8f8f2]" : "bg-white/80"}`}>
                <div>
                  <div className="font-black text-[#30343b]">{provider.name}</div>
                  <div className="text-sm font-bold text-[#8c96a6]">{provider.active ? "active" : "configured"}</div>
                </div>
                <span className={`h-4 w-4 rounded-full ${provider.healthy ? "bg-[#23c48e]" : "bg-[#cfd6df]"}`} />
              </div>
            ))}
            <div className="rounded-[22px] bg-[#2D8CFF] p-4 text-white shadow-[0_14px_30px_rgba(45,140,255,0.22)]">
              <div className="flex items-center gap-2 font-black">
                <ShieldCheck size={18} />
                Tool permissions
              </div>
              <div className="mt-2 text-sm font-bold text-white/75">{enabledTools} tools enabled, shell remains disabled by default.</div>
            </div>
          </div>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-3">
        <Card title="Memory Status">
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-[22px] bg-[#f6f8fb] p-4">
              <span className="font-black text-[#30343b]">External backend</span>
              <Pill>{memoryLabel}</Pill>
            </div>
            <div className="flex items-center justify-between rounded-[22px] bg-[#f6f8fb] p-4">
              <span className="font-black text-[#30343b]">Local items</span>
              <span className="text-2xl font-black text-[#30343b]">{memory.local_items ?? 0}</span>
            </div>
            <div className="rounded-[22px] bg-[#eaf4ff] p-4 text-sm font-bold text-[#667085]">
              TencentDB Agent Memory can be offline; PiePro keeps local fallback active.
            </div>
          </div>
        </Card>

        <Card title="Self-Update">
          <div className="space-y-3">
            <div className="rounded-[22px] bg-[#fff4d9] p-4">
              <div className="flex items-center gap-2 font-black text-[#30343b]">
                <Clock3 size={18} />
                Candidate flow
              </div>
              <div className="mt-2 text-sm font-bold text-[#8c96a6]">Plan, copy, test, healthcheck, promote, rollback.</div>
            </div>
            <div className="flex items-center justify-between rounded-[22px] bg-[#f6f8fb] p-4">
              <span className="font-black text-[#30343b]">Candidates</span>
              <span className="text-2xl font-black text-[#30343b]">{data.updates.candidates?.length ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-[22px] bg-[#f6f8fb] p-4">
              <span className="font-black text-[#30343b]">History</span>
              <span className="text-2xl font-black text-[#30343b]">{data.updates.history?.length ?? 0}</span>
            </div>
          </div>
        </Card>

        <Card title="Recent Activity">
          <div className="space-y-3">
            {activityCards.map(({ name, message, Icon }, index) => (
              <div key={name} className={`flex items-center gap-3 rounded-[22px] border border-[#e4e9f0] p-4 ${index === 0 ? "bg-[#2D8CFF] text-white shadow-[0_14px_30px_rgba(45,140,255,0.22)]" : "bg-white/80 text-[#30343b]"}`}>
                <Icon size={20} />
                <div>
                  <div className="font-black">{name}</div>
                  <div className="text-sm font-bold opacity-65">{name === "Memory" ? `${memoryLabel} mode is active.` : message}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}
