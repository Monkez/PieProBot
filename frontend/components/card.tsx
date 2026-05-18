import { ReactNode } from "react";

const toneClass = {
  white: "bg-white",
  sage: "bg-[#f3f7fb]",
  yellow: "bg-[#fff4d9]",
  blue: "bg-[#eaf4ff]",
  pink: "bg-[#fff0ea]",
  gray: "bg-[#f5f7fa]"
};

type Tone = keyof typeof toneClass;

export function Card({ title, children, tone = "white", className = "" }: { title: string; children: ReactNode; tone?: Tone; className?: string }) {
  return (
    <section className={`soft-shadow rounded-[26px] border border-[#e4e9f0] ${toneClass[tone]} p-5 ${className}`}>
      <h2 className="mb-4 text-lg font-black tracking-normal text-[#30343b]">{title}</h2>
      {children}
    </section>
  );
}

export function Stat({ label, value, tone = "white" }: { label: string; value: string | number; tone?: Tone }) {
  return (
    <div className={`soft-shadow rounded-[24px] border border-[#e4e9f0] ${toneClass[tone]} p-5`}>
      <div className="text-sm font-bold text-[#8c96a6]">{label}</div>
      <div className="mt-2 text-3xl font-black tracking-normal text-[#30343b]">{value}</div>
    </div>
  );
}

export function Pill({ children, dark = false }: { children: ReactNode; dark?: boolean }) {
  return (
    <span className={`inline-flex items-center rounded-full px-4 py-2 text-sm font-black ${dark ? "bg-[#2D8CFF] text-white shadow-[0_10px_24px_rgba(45,140,255,0.24)]" : "border border-[#e4e9f0] bg-white/80 text-[#30343b]"}`}>
      {children}
    </span>
  );
}

export function ProgressBar({ value, color = "#2D8CFF" }: { value: number; color?: string }) {
  return (
    <div className="h-3 overflow-hidden rounded-full bg-[#edf1f5]">
      <div className="h-full rounded-full" style={{ width: `${Math.max(0, Math.min(value, 100))}%`, backgroundColor: color }} />
    </div>
  );
}

export function AvatarStack({ names }: { names: string[] }) {
  const colors = ["#2D8CFF", "#75B8FF", "#FFC247", "#23C48E", "#FF8A61"];
  return (
    <div className="flex -space-x-2">
      {names.map((name, index) => (
        <div key={name} className="grid h-9 w-9 place-items-center rounded-full border-2 border-white text-xs font-black text-white" style={{ backgroundColor: colors[index % colors.length] }}>
          {name.slice(0, 1)}
        </div>
      ))}
    </div>
  );
}
