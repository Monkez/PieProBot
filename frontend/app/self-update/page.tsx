"use client";

import { Card } from "@/components/card";
import { LoadingCard } from "@/components/loading-card";
import { apiGet, apiPost } from "@/lib/api";
import { useApi } from "@/lib/use-api";
import { useState } from "react";

export default function SelfUpdatePage() {
  const { data: status, loading, error, refresh } = useApi<any>("/api/self-update/status", { candidates: [], plans: [], history: [] });
  const [goal, setGoal] = useState("Improve PiePro safely");
  const [planId, setPlanId] = useState("");
  const [candidateId, setCandidateId] = useState("");
  const [message, setMessage] = useState("");

  async function run(path: string, body: Record<string, unknown> = {}) {
    try {
      const result = await apiPost<any>(path, body);
      setMessage(JSON.stringify(result, null, 2));
      if (result.id?.startsWith?.("upd_")) setPlanId(result.id);
      if (result.id?.startsWith?.("candidate-")) setCandidateId(result.id);
      if (result.candidate_id) setCandidateId(result.candidate_id);
      await refresh();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  async function detect() {
    try {
      setMessage(JSON.stringify(await apiGet("/api/self-update/detect"), null, 2));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }

  const selectedPlan = planId || status.plans?.[0]?.id || "";
  const selectedCandidate = candidateId || status.candidates?.[0]?.id || "";

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black text-[#30343b]">Self-Update Center</h1>
      {loading ? <LoadingCard label="Loading self-update status" /> : null}
      {error ? <div className="rounded-[22px] bg-[#fff0ea] p-4 text-sm font-bold text-[#c7512f]">{error}</div> : null}
      <Card title="Candidate workflow">
        <div className="grid gap-3">
          <input value={goal} onChange={(event) => setGoal(event.target.value)} className="h-11 rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b] outline-none focus:border-[#2D8CFF]" />
          <div className="flex flex-wrap gap-2">
            <button onClick={() => run("/api/self-update/plan", { goal, files_to_change: [] })} className="h-10 rounded-full bg-[#2D8CFF] px-4 text-xs font-black text-white">Create plan</button>
            <button onClick={detect} className="h-10 rounded-full bg-[#f6f8fb] px-4 text-xs font-black text-[#667085]">Detect need</button>
            <button onClick={() => run("/api/self-update/create-candidate", { plan_id: selectedPlan })} disabled={!selectedPlan} className="h-10 rounded-full bg-[#ffc247] px-4 text-xs font-black text-white disabled:bg-[#d6dde7]">Create candidate</button>
            <button onClick={() => run("/api/self-update/test", { candidate_id: selectedCandidate })} disabled={!selectedCandidate} className="h-10 rounded-full bg-[#f6f8fb] px-4 text-xs font-black text-[#667085] disabled:opacity-50">Run tests</button>
            <button onClick={() => run("/api/self-update/start-candidate", { candidate_id: selectedCandidate })} disabled={!selectedCandidate} className="h-10 rounded-full bg-[#f6f8fb] px-4 text-xs font-black text-[#667085] disabled:opacity-50">Start</button>
            <button onClick={() => run("/api/self-update/healthcheck", { candidate_id: selectedCandidate })} disabled={!selectedCandidate} className="h-10 rounded-full bg-[#f6f8fb] px-4 text-xs font-black text-[#667085] disabled:opacity-50">Healthcheck</button>
            <button onClick={() => run("/api/self-update/promote", { candidate_id: selectedCandidate })} disabled={!selectedCandidate} className="h-10 rounded-full bg-[#23c48e] px-4 text-xs font-black text-white disabled:bg-[#d6dde7]">Promote</button>
            <button onClick={() => run("/api/self-update/rollback", { candidate_id: selectedCandidate })} disabled={!selectedCandidate} className="h-10 rounded-full bg-[#ff8a61] px-4 text-xs font-black text-white disabled:bg-[#d6dde7]">Rollback</button>
            <button onClick={() => run("/api/self-update/report", { candidate_id: selectedCandidate })} disabled={!selectedCandidate} className="h-10 rounded-full bg-[#f6f8fb] px-4 text-xs font-black text-[#667085] disabled:opacity-50">Report</button>
            <button onClick={() => run("/api/self-update/destroy", { candidate_id: selectedCandidate })} disabled={!selectedCandidate} className="h-10 rounded-full bg-[#fff0ea] px-4 text-xs font-black text-[#c7512f] disabled:opacity-50">Destroy failed</button>
          </div>
          <div className="grid gap-3 lg:grid-cols-2">
            <input value={planId} onChange={(event) => setPlanId(event.target.value)} placeholder="plan id" className="h-10 rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b]" />
            <input value={candidateId} onChange={(event) => setCandidateId(event.target.value)} placeholder="candidate id" className="h-10 rounded-full border border-[#e4e9f0] bg-white px-4 text-sm font-bold text-[#30343b]" />
          </div>
          {message ? <pre className="overflow-auto rounded-[22px] bg-[#f6f8fb] p-4 text-sm font-bold text-[#667085]">{message}</pre> : null}
        </div>
      </Card>
      <Card title="Stable and candidates">
        <pre className="overflow-auto text-sm text-[#667085]">{JSON.stringify(status, null, 2)}</pre>
      </Card>
    </div>
  );
}
