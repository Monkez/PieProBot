import { AvatarStack, Card, Pill, ProgressBar, Stat } from "@/components/card";
import { apiGet } from "@/lib/api";
import { ArrowRight, CalendarDays, CheckCircle2, Clock3, Cloud, FileText, Flame, Folder, MessageCircle, MoreVertical, Pin, Plus, Sparkles, Timer, Upload } from "lucide-react";

async function load() {
  const [health, ready, metrics, tasks, subagents, tools, providers, memory] = await Promise.all([
    apiGet<{ status: string; service?: string }>("/health").catch(() => ({ status: "offline" })),
    apiGet<{ tools: number }>("/ready").catch(() => ({ tools: 0 })),
    apiGet<Record<string, number>>("/metrics").catch(() => ({})),
    apiGet<unknown[]>("/api/tasks").catch(() => []),
    apiGet<unknown[]>("/api/subagents").catch(() => []),
    apiGet<unknown[]>("/api/tools").catch(() => []),
    apiGet<unknown[]>("/api/providers").catch(() => []),
    apiGet<{ external_enabled?: boolean; external_healthy?: boolean; local_items?: number }>("/api/memory/status").catch(() => ({ local_items: 0 }))
  ]);
  return { health, ready, metrics, tasks, subagents, tools, providers, memory };
}

const taskColumns = [
  {
    title: "Plan",
    tone: "yellow" as const,
    items: [
      { name: "Provider routing", progress: 68, priority: "High", color: "#f8c52f" },
      { name: "Config editor polish", progress: 42, priority: "Medium", color: "#ff858f" }
    ]
  },
  {
    title: "Build",
    tone: "blue" as const,
    items: [
      { name: "Subagent monitor", progress: 76, priority: "High", color: "#72b7f8" },
      { name: "Memory recall UI", progress: 58, priority: "Medium", color: "#93d7a3" }
    ]
  },
  {
    title: "Review",
    tone: "pink" as const,
    items: [
      { name: "Self-update audit", progress: 81, priority: "Careful", color: "#fb7b84" },
      { name: "Docs sync", progress: 92, priority: "Required", color: "#8c7cf3" }
    ]
  }
];

const days = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
const fileCards = [
  { name: "Docs", desc: "Updated self knowledge", color: "#ffeeb8", Icon: FileText },
  { name: "Runtime", desc: "PID and logs ready", color: "#d8edff", Icon: Folder },
  { name: "Memory", desc: "Gateway config synced", color: "#ffd7d7", Icon: Cloud }
];
const inboxCards = [
  { name: "System", message: "All checks are passing.", Icon: CheckCircle2, className: "bg-white/70 text-black" },
  { name: "Memory", message: "TencentDB gateway is optional with fallback.", Icon: BrainIcon, className: "bg-black text-white" },
  { name: "Ops", message: "Use piepro start from any directory.", Icon: Flame, className: "bg-white/70 text-black" }
];

export default async function DashboardPage() {
  const data = await load();
  const providerCount = data.providers.length;
  const toolCount = data.ready.tools || data.tools.length;
  const memory = {
    external_enabled: false,
    external_healthy: false,
    local_items: 0,
    ...data.memory
  };
  const memoryLabel = memory.external_enabled ? (memory.external_healthy ? "TencentDB" : "Fallback") : "Local";

  return (
    <div className="space-y-7">
      <section className="grid gap-4 xl:grid-cols-[1.1fr_2fr]">
        <Card title="My Profile" className="min-h-[260px]">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-4">
              <div className="grid h-16 w-16 place-items-center rounded-full border-4 border-white bg-[#c9b1ff] text-2xl font-black">P</div>
              <div>
                <div className="text-2xl font-black">PiePro</div>
                <div className="text-sm font-bold text-black/55">Agent workspace bot</div>
              </div>
            </div>
            <button className="grid h-11 w-11 place-items-center rounded-full border border-black/10 bg-white/70">
              <MoreVertical size={18} />
            </button>
          </div>
          <div className="mt-8 grid grid-cols-2 gap-3">
            <Pill>Backend {data.health.status}</Pill>
            <Pill>{memoryLabel} memory</Pill>
            <Pill>{toolCount} tools</Pill>
            <Pill>{providerCount} providers</Pill>
          </div>
          <div className="mt-8 rounded-[22px] border border-black/10 bg-[#f6f7f1] p-4">
            <div className="mb-2 flex items-center justify-between text-sm font-black">
              <span>Workspace focus</span>
              <span>82%</span>
            </div>
            <ProgressBar value={82} color="#111111" />
          </div>
        </Card>

        <Card title="Ongoing Projects" className="min-h-[260px]">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <Pill dark>Agent Sprint</Pill>
            <div className="flex gap-2">
              <button className="grid h-11 w-11 place-items-center rounded-full bg-white/80 soft-shadow"><Plus size={18} /></button>
              <button className="grid h-11 w-11 place-items-center rounded-full bg-black text-white"><Sparkles size={18} /></button>
            </div>
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            {[
              { title: "Runtime Core", tone: "yellow" as const, color: "#f5c84c", value: 78 },
              { title: "Memory Layer", tone: "blue" as const, color: "#79bdf8", value: 64 },
              { title: "Admin UI", tone: "pink" as const, color: "#fb858f", value: 71 }
            ].map((project) => (
              <div key={project.title} className={`rounded-[24px] border border-black/10 p-5 ${project.tone === "yellow" ? "bg-[#ffeeb8]" : project.tone === "blue" ? "bg-[#d4ebff]" : "bg-[#ffd7d7]"}`}>
                <div className="mb-5 flex items-center justify-between">
                  <Pill>May 2026</Pill>
                  <MoreVertical size={18} />
                </div>
                <div className="text-xl font-black">{project.title}</div>
                <div className="mt-4 flex items-center gap-2 text-sm font-bold">
                  <span>Progress</span>
                  <Pill>{project.value}%</Pill>
                </div>
                <div className="mt-4"><ProgressBar value={project.value} color={project.color} /></div>
                <div className="mt-5 flex items-center justify-between">
                  <AvatarStack names={["A", "B", "C"]} />
                  <Pill>+2 days</Pill>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <Stat label="Tasks" value={data.tasks.length} tone="yellow" />
        <Stat label="Subagents" value={data.subagents.length} tone="blue" />
        <Stat label="Tools" value={toolCount} tone="pink" />
        <Stat label="Providers" value={providerCount} tone="sage" />
        <Stat label="Local Memory" value={memory.local_items ?? 0} tone="gray" />
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.2fr_0.9fr_1fr]">
        <Card title="Task Management">
          <div className="grid gap-3 lg:grid-cols-3">
            {taskColumns.map((column) => (
              <div key={column.title} className="rounded-[24px] bg-white/55 p-3">
                <div className="mb-3 flex items-center justify-between">
                  <Pill dark>{column.title}</Pill>
                  <span className="text-sm font-black text-black/45">{column.items.length}</span>
                </div>
                <div className="space-y-3">
                  {column.items.map((task) => (
                    <div key={task.name} className={`rounded-[22px] border border-black/10 p-4 ${column.tone === "yellow" ? "bg-[#fff1be]" : column.tone === "blue" ? "bg-[#d8edff]" : "bg-[#ffdada]"}`}>
                      <div className="mb-3 flex items-start justify-between">
                        <div className="text-base font-black">{task.name}</div>
                        <span className="h-3 w-3 rounded-full" style={{ backgroundColor: task.color }} />
                      </div>
                      <div className="mb-3 flex items-center justify-between text-xs font-black text-black/55">
                        <span>{task.priority}</span>
                        <span>{task.progress}%</span>
                      </div>
                      <ProgressBar value={task.progress} color={task.color} />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Calendar">
          <div className="mb-4 flex items-center justify-between">
            <button className="grid h-10 w-10 place-items-center rounded-full bg-white soft-shadow"><ArrowRight className="rotate-180" size={17} /></button>
            <div className="text-xl font-black">May</div>
            <button className="grid h-10 w-10 place-items-center rounded-full bg-white soft-shadow"><ArrowRight size={17} /></button>
          </div>
          <div className="grid grid-cols-6 gap-2">
            {days.map((day) => {
              const active = day === 11 ? "bg-[#87c4ff]" : day === 27 ? "bg-[#ffc82e]" : day === 30 ? "bg-[#5e62d9] text-white" : day === 5 ? "bg-[#ff7f88] text-white" : [13, 16, 29].includes(day) ? "bg-[#555555] text-white" : "bg-[#deded9]";
              return <div key={day} className={`grid aspect-square place-items-center rounded-xl text-base font-black ${active}`}>{day}</div>;
            })}
          </div>
        </Card>

        <Card title="Team Collaboration">
          <div className="space-y-3">
            {[
              ["Mia", "Online", "#89d99a"],
              ["Robert", "Reviewing task plan", "#87c4ff"],
              ["Esther", "Offline", "#d0d0cb"],
              ["Darrell", "In focus mode", "#ffcd4b"]
            ].map(([name, status, color], index) => (
              <div key={name} className={`flex items-center justify-between rounded-[20px] border border-black/10 p-3 ${index === 1 ? "bg-black text-white" : "bg-white/70"}`}>
                <div className="flex items-center gap-3">
                  <div className="relative grid h-11 w-11 place-items-center rounded-full bg-[#ffd7d7] font-black">
                    {name.slice(0, 1)}
                    <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white" style={{ backgroundColor: color }} />
                  </div>
                  <div>
                    <div className="font-black">{name}</div>
                    <div className={`text-xs font-bold ${index === 1 ? "text-white/70" : "text-black/50"}`}>{status}</div>
                  </div>
                </div>
                <MessageCircle size={18} />
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-4">
        <Card title="Analytics Overview" tone="blue" className="xl:col-span-2">
          <div className="grid gap-4 sm:grid-cols-3">
            {[
              ["Focus", "7.8h", 82, "#111111"],
              ["Resolved", "24", 74, "#ff858f"],
              ["Recall", "91%", 91, "#5e62d9"]
            ].map(([label, value, progress, color]) => (
              <div key={label} className="rounded-[24px] bg-white/65 p-4">
                <div className="text-sm font-black text-black/50">{label}</div>
                <div className="mt-2 text-3xl font-black">{value}</div>
                <div className="mt-5"><ProgressBar value={Number(progress)} color={String(color)} /></div>
              </div>
            ))}
          </div>
          <div className="mt-5 flex h-28 items-end gap-3 rounded-[24px] bg-white/55 p-4">
            {[48, 72, 56, 88, 64, 92, 78].map((height, index) => (
              <div key={index} className="flex-1 rounded-t-2xl bg-black/85" style={{ height: `${height}%` }} />
            ))}
          </div>
        </Card>

        <Card title="Time Tracking" tone="yellow">
          <div className="grid place-items-center py-2">
            <div className="grid h-36 w-36 place-items-center rounded-full border-[14px] border-black bg-[#fff8d8]">
              <div className="text-center">
                <Timer className="mx-auto mb-1" size={23} />
                <div className="text-3xl font-black">42m</div>
                <div className="text-xs font-black text-black/50">Focus mode</div>
              </div>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2 text-center text-sm font-black">
            <div className="rounded-full bg-white/70 px-3 py-2">3 sessions</div>
            <div className="rounded-full bg-white/70 px-3 py-2">Calm</div>
          </div>
        </Card>

        <Card title="Mobile App" tone="pink">
          <div className="mx-auto w-40 rounded-[30px] border-4 border-black bg-[#f8f8f2] p-3">
            <div className="mb-3 h-4 rounded-full bg-black/15" />
            <div className="rounded-[20px] bg-[#d8edff] p-3 text-center text-sm font-black">PiePro Pocket</div>
            <div className="mt-3 space-y-2">
              <div className="h-9 rounded-full bg-[#ffeeb8]" />
              <div className="h-9 rounded-full bg-[#ffd7d7]" />
              <div className="h-9 rounded-full bg-black" />
            </div>
          </div>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1fr_1fr_1fr]">
        <Card title="Notes & Sticky Board">
          <div className="grid grid-cols-2 gap-3">
            {[
              ["Docs are runtime memory", "bg-[#fff0b8] rotate-[-2deg]"],
              ["Keep self-update safe", "bg-[#d8edff] rotate-[2deg]"],
              ["Memory fallback required", "bg-[#ffd7d7] rotate-[-1deg]"],
              ["No Docker required", "bg-[#dff0df] rotate-[1deg]"]
            ].map(([text, cls]) => (
              <div key={text} className={`min-h-28 rounded-[20px] p-4 text-sm font-black shadow-sm ${cls}`}>
                <Pin size={16} className="mb-3" />
                {text}
              </div>
            ))}
          </div>
        </Card>

        <Card title="File Manager">
          <div className="space-y-3">
            {fileCards.map(({ name, desc, color, Icon }) => (
              <div key={name} className="flex items-center gap-3 rounded-[22px] border border-black/10 bg-white/70 p-3">
                <div className="grid h-12 w-12 place-items-center rounded-2xl" style={{ backgroundColor: color }}>
                  <Icon size={20} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="font-black">{name}</div>
                  <div className="truncate text-sm font-bold text-black/50">{desc}</div>
                </div>
                <Upload size={18} />
              </div>
            ))}
          </div>
        </Card>

        <Card title="Settings & Personalization">
          <div className="space-y-4">
            <div className="rounded-[22px] bg-white/70 p-4">
              <div className="mb-3 flex items-center justify-between font-black">
                <span>Theme</span>
                <Pill>Soft sage</Pill>
              </div>
              <div className="flex gap-2">
                {["#dfece3", "#ffeeb8", "#d4ebff", "#ffd7d7"].map((color) => (
                  <div key={color} className="h-10 flex-1 rounded-full border-2 border-black/80" style={{ backgroundColor: color }} />
                ))}
              </div>
            </div>
            <div className="flex items-center justify-between rounded-full bg-white/70 p-2 pl-5 font-black">
              <span>Docs sync</span>
              <span className="rounded-full bg-black px-5 py-3 text-white">On</span>
            </div>
            <div className="flex items-center justify-between rounded-full bg-white/70 p-2 pl-5 font-black">
              <span>Focus mode</span>
              <span className="rounded-full bg-[#ffeeb8] px-5 py-3">Ready</span>
            </div>
          </div>
        </Card>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <Card title="Inbox">
          <div className="space-y-3">
            {inboxCards.map(({ name, message, Icon, className }) => (
              <div key={name} className={`flex items-center gap-3 rounded-[22px] border border-black/10 p-4 ${className}`}>
                <Icon size={20} />
                <div>
                  <div className="font-black">{name}</div>
                  <div className="text-sm font-bold opacity-70">{message}</div>
                </div>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Runtime Metrics">
          <pre className="max-h-64 overflow-auto rounded-[22px] bg-white/70 p-4 text-sm font-bold text-black/65">{JSON.stringify(data.metrics, null, 2)}</pre>
        </Card>
      </section>
    </div>
  );
}

function BrainIcon(props: { size?: number }) {
  return <Clock3 {...props} />;
}
