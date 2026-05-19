from __future__ import annotations


class ContextEngine:
    """Small message compactor for long agent loops."""

    def __init__(self, max_messages: int = 18, protect_head: int = 2, protect_tail: int = 8) -> None:
        self.max_messages = max_messages
        self.protect_head = protect_head
        self.protect_tail = protect_tail
        self.compression_count = 0

    def compact(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        if len(messages) <= self.max_messages:
            return messages
        head = messages[: self.protect_head]
        tail = messages[-self.protect_tail :]
        middle = messages[self.protect_head : -self.protect_tail]
        summary_bits = []
        for msg in middle:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            summary_bits.append(f"{role}: {content[:240]}")
        summary = {
            "role": "system",
            "content": "[Compressed prior context]\n" + "\n".join(summary_bits)[-6000:],
        }
        self.compression_count += 1
        return [*head, summary, *tail]
