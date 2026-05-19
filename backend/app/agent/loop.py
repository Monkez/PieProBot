from __future__ import annotations

import json
import re
from typing import Any

from app.agent.context_engine import ContextEngine
from app.agent.system_prompt import SystemPromptBuilder
from app.core.task_model import SubagentRecord, SubagentStatus
from app.providers.router import ProviderRouter
from app.tools.registry import ToolRegistry


TOOL_BLOCK_RE = re.compile(r"<tool_calls>\s*(\{[\s\S]*?\})\s*</tool_calls>", re.IGNORECASE)


class AgentLoop:
    def __init__(
        self,
        *,
        root,
        provider_router: ProviderRouter,
        tool_registry: ToolRegistry,
        memory=None,
        skills=None,
        max_iterations: int = 6,
    ) -> None:
        self.provider_router = provider_router
        self.tool_registry = tool_registry
        self.prompt_builder = SystemPromptBuilder(root, memory=memory, skills=skills, tool_registry=tool_registry)
        self.context_engine = ContextEngine()
        self.max_iterations = max_iterations

    async def run(self, record: SubagentRecord) -> str:
        goal = str(record.context.get("goal", ""))
        system_prompt = await self.prompt_builder.build(
            task_goal=goal,
            agent_type=record.type,
            allowed_tools=record.allowed_tools,
            allowed_toolsets=record.allowed_toolsets,
            context=record.context,
        )
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": goal},
        ]
        final_content = ""

        for iteration in range(min(record.tool_call_budget, self.max_iterations)):
            record.heartbeat(f"agent loop {iteration + 1}")
            response = await self.provider_router.chat(messages)
            final_content = response.content
            tool_calls = self._parse_tool_calls(response.content)
            if not tool_calls:
                break

            messages.append({"role": "assistant", "content": response.content})
            for call in tool_calls:
                name = str(call.get("name", ""))
                args = call.get("arguments") if isinstance(call.get("arguments"), dict) else {}
                if name not in record.allowed_tools:
                    result = {"ok": False, "error": f"Tool not allowed: {name}"}
                else:
                    record.status = SubagentStatus.WAITING_FOR_TOOL
                    tool_result = await self.tool_registry.execute(
                        name,
                        args,
                        granted_permissions=record.permissions,
                        task_id=record.task_id,
                        subagent_id=record.id,
                    )
                    result = tool_result.model_dump(mode="json")
                    record.status = SubagentStatus.RUNNING
                messages.append({"role": "tool", "content": json.dumps({"tool": name, "result": result}, ensure_ascii=False)})
            messages = self.context_engine.compact(messages)
        return final_content

    @staticmethod
    def _parse_tool_calls(content: str) -> list[dict[str, Any]]:
        text = content.strip()
        candidates = [text]
        match = TOOL_BLOCK_RE.search(text)
        if match:
            candidates.insert(0, match.group(1))
        if "```json" in text:
            try:
                candidates.insert(0, text.split("```json", 1)[1].split("```", 1)[0])
            except IndexError:
                pass
        for candidate in candidates:
            try:
                data = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            calls = data.get("tool_calls") if isinstance(data, dict) else None
            if isinstance(calls, list):
                return [call for call in calls if isinstance(call, dict)]
        return []
