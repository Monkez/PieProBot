from __future__ import annotations

from app.memory.manager import MemoryItem, MemoryManager


async def test_memory_save_search_compact() -> None:
    memory = MemoryManager()
    await memory.save(MemoryItem(content="project prefers lightweight deploys", importance=0.7))
    await memory.save(MemoryItem(content="project prefers lightweight deploys", importance=0.7))
    results = await memory.search("lightweight")
    assert len(results) == 1
    summary = await memory.compact()
    assert summary["after"] == 1


class FakeExternalMemory:
    base_url = "http://fake-memory"

    def __init__(self) -> None:
        self.captured = False

    async def search_memories(self, query: str, limit: int):
        return [MemoryItem(type="tencentdb_memory", content=f"external result for {query}", source="fake")]

    async def search_conversations(self, query: str, limit: int):
        return []

    async def capture_turn(self, **kwargs):
        self.captured = True
        return {"l0_recorded": 2}

    async def health(self):
        return {"status": "ok"}


class FailingExternalMemory(FakeExternalMemory):
    async def search_memories(self, query: str, limit: int):
        raise RuntimeError("gateway down")

    async def capture_turn(self, **kwargs):
        raise RuntimeError("gateway down")

    async def health(self):
        raise RuntimeError("gateway down")


async def test_memory_uses_tencentdb_external_backend_when_available() -> None:
    external = FakeExternalMemory()
    memory = MemoryManager(external_backend=external)
    capture = await memory.capture_turn(user_content="remember me", assistant_content="stored", session_id="task_1")
    assert capture["captured"] == "tencentdb-agent-memory"
    assert external.captured is True
    results = await memory.search("preference")
    assert results[0].type == "tencentdb_memory"
    assert "external result" in results[0].content
    assert (await memory.status())["external_healthy"] is True


async def test_memory_falls_back_to_local_when_tencentdb_gateway_fails() -> None:
    memory = MemoryManager(external_backend=FailingExternalMemory())
    await memory.save(MemoryItem(content="local fallback survives"))
    capture = await memory.capture_turn(user_content="hello", assistant_content="world", session_id="task_2")
    assert capture["captured"] == "local"
    results = await memory.search("fallback")
    assert len(results) >= 1
    assert any("local fallback survives" in item.content for item in results)
    assert (await memory.status())["external_healthy"] is False
