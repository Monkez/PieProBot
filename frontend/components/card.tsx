import { ReactNode } from "react";

const toneClass = {
  white: "bg-[#fbfbf4]",
  sage: "bg-[#edf6ee]",
  yellow: "bg-[#ffeeb8]",
  blue: "bg-[#d4ebff]",
  pink: "bg-[#ffd7d7]",
  gray: "bg-[#f1f2ee]"
};

type Tone = keyof typeof toneClass;

export function Card({ title, children, tone = "white", className = "" }: { title: string; children: ReactNode; tone?: Tone; className?: string }) {
  return (
    <section className={`soft-shadow rounded-[26px] border border-black/10 ${toneClass[tone]} p-5 ${className}`}>
      <h2 className="mb-4 text-lg font-black tracking-normal text-black">{title}</h2>
      {children}
    </section>
  );
}

export function Stat({ label, value, tone = "white" }: { label: string; value: string | number; tone?: Tone }) {
  return (
    <div className={`soft-shadow rounded-[24px] border border-black/10 ${toneClass[tone]} p-5`}>
      <div className="text-sm font-bold text-black/55">{label}</div>
      <div className="mt-2 text-3xl font-black tracking-normal text-black">{value}</div>
    </div>
  );
}

export function Pill({ children, dark = false }: { children: ReactNode; dark?: boolean }) {
  return (
    <span className={`inline-flex items-center rounded-full px-4 py-2 text-sm font-black ${dark ? "bg-black text-white" : "border border-black/10 bg-white/70 text-black"}`}>
      {children}
    </span>
  );
}

export function ProgressBar({ value, color = "#111111" }: { value: number; color?: string }) {
  return (
    <div className="h-3 overflow-hidden rounded-full bg-white/70">
      <div className="h-full rounded-full" style={{ width: `${Math.max(0, Math.min(value, 100))}%`, backgroundColor: color }} />
    </div>
  );
}

export function AvatarStack({ names }: { names: string[] }) {
  const colors = ["#ff858f", "#7ebcf8", "#ffd050", "#bca7ff", "#93d7a3"];
  return (
    <div className="flex -space-x-2">
      {names.map((name, index) => (
        <div key={name} className="grid h-9 w-9 place-items-center rounded-full border-2 border-white text-xs font-black text-black" style={{ backgroundColor: colors[index % colors.length] }}>
          {name.slice(0, 1)}
        </div>
      ))}
    </div>
  );
}
