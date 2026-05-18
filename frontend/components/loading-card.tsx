export function LoadingCard({ label = "Loading" }: { label?: string }) {
  return (
    <div className="soft-shadow rounded-[24px] border border-[#e4e9f0] bg-white p-5 text-sm font-bold text-[#8c96a6]">
      {label}...
    </div>
  );
}
