from __future__ import annotations

import logging
import time
from contextlib import AbstractContextManager
from typing import Self

from app.config import settings

logger = logging.getLogger(__name__)


class AgentTracer(AbstractContextManager["AgentTracer"]):
    """Structured agent telemetry — stdout logs locally, App Insights when configured."""

    def __init__(
        self,
        *,
        conversation_id: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.conversation_id = conversation_id
        self.request_id = request_id
        self._spans: dict[str, float] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def start_span(self, name: str) -> None:
        self._spans[name] = time.perf_counter()
        self._emit("span_start", span=name)

    def end_span(self, name: str, **extra: object) -> None:
        started = self._spans.pop(name, None)
        duration_ms = round((time.perf_counter() - started) * 1000, 1) if started else None
        self._emit("span_end", span=name, duration_ms=duration_ms, **extra)

    def log_tool(self, tool: str, duration_ms: float) -> None:
        self._emit("tool_call", tool=tool, duration_ms=round(duration_ms, 1))

    def log_tokens(self, *, prompt: int, completion: int) -> None:
        self._emit("token_usage", prompt_tokens=prompt, completion_tokens=completion)

    def _emit(self, event: str, **fields: object) -> None:
        payload = {
            "event": event,
            "conversation_id": self.conversation_id,
            "request_id": self.request_id,
            **{k: v for k, v in fields.items() if v is not None},
        }
        logger.info("telemetry %s", payload)

        if not settings.insights_configured:
            return

        try:
            from opentelemetry import trace

            tracer = trace.get_tracer("enterprise-api.agent")
            with tracer.start_as_current_span(event) as span:
                for key, value in payload.items():
                    if key != "event":
                        span.set_attribute(key, str(value))
        except Exception as exc:  # noqa: BLE001
            logger.debug("OpenTelemetry span skipped: %s", exc)
