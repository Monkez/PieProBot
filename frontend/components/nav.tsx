"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Bot, Boxes, Brain, FileCog, Hammer, Home, LayoutDashboard, Mail, MessageSquare, Radio, Search, Server, ShieldCheck, UserRound } from "lucide-react";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/tasks", label: "Tasks", icon: Boxes },
  { href: "/subagents", label: "Subagents", icon: Bot },
  { href: "/tools", label: "Tools", icon: Hammer },
  { href: "/providers", label: "Providers", icon: Server },
  { href: "/channels", label: "Channels", icon: Radio },
  { href: "/memory", label: "Memory", icon: Brain },
  { href: "/self-update", label: "Self Update", icon: ShieldCheck },
  { href: "/logs", label: "Logs", icon: LayoutDashboard },
  { href: "/config", label: "Config", icon: FileCog }
];

export function TopBar() {
  const pathname = usePathname();
  return (
    <header className="mb-7 flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <button className="grid h-12 w-12 place-items-center rounded-full bg-white text-[#2D8CFF] soft-shadow" aria-label="Menu">
          <LayoutDashboard size={20} />
        </button>
        <div>
          <div className="text-3xl font-black tracking-normal text-[#30343b]">PiePro</div>
          <div className="text-sm font-bold text-[#9aa3af]">Premium local agent workspace</div>
        </div>
      </div>
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <nav className="flex max-w-full gap-2 overflow-x-auto rounded-[28px] border border-[#e4e9f0] bg-white/85 p-2 soft-shadow">
          {items.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link key={item.label} href={item.href} className={`inline-flex h-11 shrink-0 items-center gap-2 rounded-full px-4 text-sm font-black transition ${active ? "bg-[#2D8CFF] text-white shadow-[0_10px_24px_rgba(45,140,255,0.22)]" : "bg-[#f6f8fb] text-[#667085] hover:bg-[#edf5ff] hover:text-[#2D8CFF]"}`}>
                <Icon size={16} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="flex items-center gap-2">
          {[Mail, Bell, Search].map((Icon, index) => (
            <button key={index} className="grid h-11 w-11 place-items-center rounded-full bg-white text-[#9aa3af] soft-shadow" aria-label="Action">
              <Icon size={18} />
            </button>
          ))}
          <div className="grid h-12 w-12 place-items-center rounded-full border-2 border-white bg-[#ffc247] text-white shadow-md">
            <UserRound size={21} />
          </div>
        </div>
      </div>
    </header>
  );
}
