import Link from "next/link";
import { Bell, Bot, Boxes, Brain, FileCog, Hammer, Home, LayoutDashboard, Mail, MessageSquare, Search, Server, Settings, ShieldCheck, UserRound } from "lucide-react";

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

export function Nav() {
  return (
    <aside className="hidden w-[74px] shrink-0 py-24 lg:block">
      <nav className="sticky top-24 flex flex-col items-center gap-3 rounded-full bg-black p-3 shadow-[0_18px_40px_rgba(0,0,0,0.18)]">
        {items.slice(0, 8).map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.href + item.label} href={item.href} title={item.label} className="grid h-11 w-11 place-items-center rounded-full bg-white/15 text-white transition hover:bg-white hover:text-black">
              <Icon size={19} />
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

export function TopBar() {
  return (
    <header className="mb-7 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="flex items-center gap-3">
        <button className="grid h-12 w-12 place-items-center rounded-full bg-white/80 text-black soft-shadow" aria-label="Menu">
          <LayoutDashboard size={20} />
        </button>
        <div>
          <div className="text-3xl font-black tracking-normal">PiePro</div>
          <div className="text-sm font-bold text-black/50">Soft agent workspace</div>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2 rounded-full border border-black/10 bg-white/70 p-2 soft-shadow">
        {[
          { href: "/dashboard", label: "Home", icon: Home },
          { href: "/tasks", label: "Tasks", icon: Boxes },
          { href: "/providers", label: "Providers", icon: Server },
          { href: "/config", label: "Settings", icon: Settings }
        ].map((item, index) => {
          const Icon = item.icon;
          return (
            <Link key={item.label} href={item.href} className={`inline-flex h-10 items-center gap-2 rounded-full px-4 text-sm font-black ${index === 1 ? "bg-black text-white" : "bg-white/80 text-black"}`}>
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </div>
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
    </header>
  );
}
