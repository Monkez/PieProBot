import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function ConfigPage() {
  const config = await apiGet<{ files: string[] }>("/api/config").catch(() => ({ files: [] }));
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Config Editor</h1>
      <Card title="Config files">
        <ul className="space-y-2 text-sm text-slate-300">
          {config.files.map((file) => <li key={file} className="rounded-md border border-line bg-slate-950 p-2">{file}</li>)}
        </ul>
      </Card>
    </div>
  );
}

