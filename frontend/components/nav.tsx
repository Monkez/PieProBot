import Link from "next/link";
import { Bell, Bot, Boxes, Brain, FileCog, Hammer, Home, LayoutDashboard, Mail, MessageSquare, Search, Server, ShieldCheck, UserRound } from "lucide-react";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/tasks", label: "Tasks", icon: Boxes },
  { href: "/subagents", label: "Subagents", icon: Bot },
  { href: "/tools", label: "Tools", icon: Hammer },
  { href: "/providers", label: "Providers", icon: Server },
  { href: "/memory", label: "Memory", icon: Brain },
  { href: "/self-update", label: "Self Update", icon: ShieldCheck },
  { href: "/logs", label: "Logs", icon: LayoutDashboard },
  { href: "/config", label: "Config", icon: FileCog }
];

export function TopBar() {
  return (
    <header className="mb-7 flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <button className="grid h-12 w-12 place-items-center rounded-full bg-white/80 text-black soft-shadow" aria-label="Menu">
          <LayoutDashboard size={20} />
        </button>
        <div>
          <div className="text-3xl font-black tracking-normal">PiePro</div>
          <div className="text-sm font-bold text-black/50">Soft agent workspace</div>
        </div>
      </div>
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <nav className="flex max-w-full gap-2 overflow-x-auto rounded-[28px] border border-black/10 bg-white/70 p-2 soft-shadow">
          {items.map((item, index) => {
            const Icon = item.icon;
            return (
              <Link key={item.label} href={item.href} className={`inline-flex h-11 shrink-0 items-center gap-2 rounded-full px-4 text-sm font-black ${index === 0 ? "bg-black text-white" : "bg-white/80 text-black"}`}>
                <Icon size={16} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="flex items-center gap-2">
          {[Mail, Bell, Search].map((Icon, index) => (
            <button key={index} className="grid h-11 w-11 place-items-center rounded-full bg-white/80 text-black soft-shadow" aria-label="Action">
              <Icon size={18} />
            </button>
          ))}
          <div className="grid h-12 w-12 place-items-center rounded-full border-2 border-white bg-[#c9b1ff] text-black shadow-md">
            <UserRound size={21} />
          </div>
        </div>
      </div>
    </header>
  );
}
