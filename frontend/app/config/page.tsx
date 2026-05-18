import { Card } from "@/components/card";
import { ConfigEditor } from "@/components/config-editor";
import { apiGet } from "@/lib/api";

export default async function ConfigPage() {
  const config = await apiGet<{ files: string[] }>("/api/config").catch(() => ({ files: [] }));
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Config Editor</h1>
      <Card title="Editable runtime config">
        <ConfigEditor files={config.files} />
      </Card>
    </div>
  );
}
