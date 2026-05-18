import Link from "next/link";
import { Activity, Bot, Boxes, Brain, FileCog, Hammer, LayoutDashboard, MessageSquare, Server, ScrollText, ShieldCheck } from "lucide-react";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/tasks", label: "Tasks", icon: Boxes },
  { href: "/subagents", label: "Subagents", icon: Bot },
  { href: "/tools", label: "Tools", icon: Hammer },
  { href: "/providers", label: "Providers", icon: Server },
  { href: "/memory", label: "Memory", icon: Brain },
  { href: "/self-update", label: "Self Update", icon: ShieldCheck },
  { href: "/logs", label: "Logs", icon: ScrollText },
  { href: "/config", label: "Config", icon: FileCog },
  { href: "/dashboard", label: "Metrics", icon: Activity }
];

export function Nav() {
  return (
    <aside className="hidden min-h-screen w-64 border-r border-line bg-panel p-4 lg:block">
      <div className="mb-8">
        <div className="text-xl font-semibold tracking-normal">PiePro</div>
        <div className="text-sm text-slate-400">Agent operations console</div>
      </div>
      <nav className="space-y-1">
        {items.slice(0, 10).map((item) => {
          const Icon = item.icon;
          return (
            <Link key={item.href + item.label} href={item.href} className="flex h-10 items-center gap-3 rounded-md px-3 text-sm text-slate-300 hover:bg-slate-800 hover:text-white">
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
