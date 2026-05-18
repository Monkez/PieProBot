import { Card } from "@/components/card";
import { apiGet } from "@/lib/api";

export default async function TasksPage() {
  const tasks = await apiGet<any[]>("/api/tasks").catch(() => []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Task Manager</h1>
      <Card title="Tasks">
        <div className="overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[#8c96a6]"><tr><th className="p-2">ID</th><th>Status</th><th>Subagents</th><th>Message</th></tr></thead>
            <tbody className="text-[#30343b]">{tasks.map((task) => <tr key={task.id} className="border-t border-[#e4e9f0]"><td className="p-2">{task.id}</td><td>{task.status}</td><td>{task.assigned_subagents?.length || 0}</td><td>{task.message}</td></tr>)}</tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
