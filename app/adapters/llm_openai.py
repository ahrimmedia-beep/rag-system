import json
from typing import Any

from app.domain.models import LLMResult, Message, ToolCall


class OpenAILLM:
    def __init__(self, base_url: str, api_key: str, model: str, client: Any | None = None) -> None:
        if client is None:
            from openai import OpenAI

            client = OpenAI(base_url=base_url, api_key=api_key)
        self._client = client
        self._model = model

    def chat(
        self,
        system: str,
        messages: list[Message],
        tools: list[dict[str, object]] | None = None,
    ) -> LLMResult:
        payload: list[dict[str, object]] = [{"role": "system", "content": system}]
        payload.extend({"role": m.role, "content": m.content} for m in messages)
        kwargs: dict[str, object] = {"model": self._model, "messages": payload}
        if tools:
            kwargs["tools"] = tools
        resp = self._client.chat.completions.create(**kwargs)  # type: ignore[call-overload]
        msg = resp.choices[0].message
        tool_calls = [
            ToolCall(
                id=tc.id,
                name=tc.function.name,
                arguments=json.loads(tc.function.arguments or "{}"),
            )
            for tc in (msg.tool_calls or [])
        ]
        return LLMResult(content=msg.content, tool_calls=tool_calls)
