import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function ConfigPage() {
  const config = await apiGet<{ files: string[] }>("/api/config").catch(() => ({ files: [] }));
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Config Editor</h1>
      <Card title="Config files">
        <ul className="space-y-2 text-sm font-bold text-black/70">
          {config.files.map((file) => <li key={file} className="rounded-[18px] border border-black/10 bg-white/70 p-3">{file}</li>)}
        </ul>
      </Card>
    </div>
  );
}
