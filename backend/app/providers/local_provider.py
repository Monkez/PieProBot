from __future__ import annotations

from app.providers.base import BaseLLMProvider, ProviderResponse


class LocalProvider(BaseLLMProvider):
    name = "local"

    async def chat(self, messages: list[dict[str, str]], model: str | None = None) -> ProviderResponse:
        latest = messages[-1]["content"] if messages else ""
        content = self._fallback_response(latest)
        return ProviderResponse(
            content=content,
            model=model or "local-mock",
            input_tokens=sum(len(m.get("content", "").split()) for m in messages),
            output_tokens=max(1, len(content.split())),
        )

    def _fallback_response(self, latest: str) -> str:
        text = latest.strip()
        lowered = text.lower()
        if lowered in {"hi", "hello", "hey", "xin chào", "chào", "chao", "alo"}:
            return "Xin chào. Tôi đang chạy ở chế độ local fallback. Hãy bật một provider thật trong trang Providers để tôi trả lời bằng mô hình AI đầy đủ."
        if "attached files:" in lowered:
            return "Tôi đã nhận được nội dung và tệp đính kèm. Hiện runtime đang dùng local fallback nên tôi chỉ ghi nhận metadata; hãy bật provider thật để phân tích nội dung chi tiết."
        if not text:
            return "Tôi đã sẵn sàng. Hãy nhập tin nhắn hoặc bật provider thật để sử dụng phản hồi AI đầy đủ."
        return f"Tôi đã nhận được: {text}\n\nHiện PiePro đang dùng local fallback, nên phản hồi này chỉ xác nhận tác vụ. Bật provider thật trong Providers để nhận câu trả lời AI đầy đủ."
