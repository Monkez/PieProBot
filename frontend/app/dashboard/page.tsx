import { Card, Stat } from "@/components/card";
import { apiGet } from "@/lib/api";

async function load() {
  const [health, ready, metrics, tasks, subagents, tools, providers] = await Promise.all([
    apiGet<{ status: string }>("/health").catch(() => ({ status: "offline" })),
    apiGet<{ tools: number }>("/ready").catch(() => ({ tools: 0 })),
    apiGet<Record<string, number>>("/metrics").catch(() => ({})),
    apiGet<unknown[]>("/api/tasks").catch(() => []),
    apiGet<unknown[]>("/api/subagents").catch(() => []),
    apiGet<unknown[]>("/api/tools").catch(() => []),
    apiGet<unknown[]>("/api/providers").catch(() => [])
  ]);
  return { health, ready, metrics, tasks, subagents, tools, providers };
}

export default async function DashboardPage() {
  const data = await load();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <p className="text-sm text-slate-400">Runtime status, active work, tools, providers and resource indicators.</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <Stat label="Backend" value={data.health.status} />
        <Stat label="Tasks" value={data.tasks.length} />
        <Stat label="Subagents" value={data.subagents.length} />
        <Stat label="Tools" value={data.ready.tools || data.tools.length} />
        <Stat label="Providers" value={data.providers.length} />
      </div>
      <Card title="Metrics">
        <pre className="overflow-auto text-sm text-slate-300">{JSON.stringify(data.metrics, null, 2)}</pre>
      </Card>
    </div>
  );
}

