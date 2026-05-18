"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
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

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  useEffect(() => {
    items.forEach((item) => router.prefetch(item.href));
  }, [router]);
  return (
    <aside className="flex h-full flex-col gap-5 rounded-[28px] border border-[#e4e9f0] bg-white/90 p-4 soft-shadow">
      <div className="flex items-center gap-3 px-1">
        <div className="grid h-12 w-12 place-items-center rounded-full bg-[#2D8CFF] text-xl font-black text-white shadow-[0_10px_24px_rgba(45,140,255,0.22)]">P</div>
        <div className="min-w-0">
          <div className="text-2xl font-black tracking-normal text-[#30343b]">PiePro</div>
          <div className="truncate text-xs font-bold text-[#9aa3af]">Local agent OS</div>
        </div>
      </div>
      <nav className="grid gap-2 overflow-y-auto pr-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link key={item.label} href={item.href} className={`inline-flex h-12 items-center gap-3 rounded-[18px] px-4 text-sm font-black transition ${active ? "bg-[#2D8CFF] text-white shadow-[0_10px_24px_rgba(45,140,255,0.22)]" : "bg-[#f6f8fb] text-[#667085] hover:bg-[#edf5ff] hover:text-[#2D8CFF]"}`}>
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto space-y-3 rounded-[24px] bg-[#f6f8fb] p-3">
        <div className="flex items-center gap-2">
          {[Mail, Bell, Search].map((Icon, index) => (
            <button key={index} className="grid h-10 w-10 place-items-center rounded-full bg-white text-[#9aa3af] soft-shadow" aria-label="Action">
              <Icon size={16} />
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3 rounded-[18px] bg-white p-2">
          <div className="grid h-10 w-10 place-items-center rounded-full bg-[#ffc247] text-white shadow-md">
            <UserRound size={18} />
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-black text-[#30343b]">Local Admin</div>
            <div className="text-xs font-bold text-[#9aa3af]">operator</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
