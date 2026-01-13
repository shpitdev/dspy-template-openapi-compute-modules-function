"""Callback handlers for DSPy runtime events."""

from __future__ import annotations

import logging
from typing import Any

from dspy.utils.callback import BaseCallback

logger = logging.getLogger("dspy.llm")


class LLMRequestLoggingCallback(BaseCallback):
    """Log the raw LM prompt/messages sent to the provider."""

    def on_lm_start(self, call_id: str, instance: Any, inputs: dict[str, Any]):
        prompt = inputs.get("prompt")
        messages = inputs.get("messages")
        if messages is None and prompt is not None:
            messages = [{"role": "user", "content": prompt}]
        prompt_breakdown = _build_prompt_breakdown(messages)
        kwargs = {key: value for key, value in inputs.items() if key not in {"prompt", "messages"}}
        merged_kwargs = {**getattr(instance, "kwargs", {}), **kwargs}
        request_payload = {
            **merged_kwargs,
            "model": getattr(instance, "model", None),
            "messages": messages,
        }
        extra = {
            "event": "llm_request",
            "call_id": call_id,
            "model": getattr(instance, "model", None),
            "model_type": getattr(instance, "model_type", None),
            "request": request_payload,
            "prompt_breakdown": prompt_breakdown,
        }

        if messages is not None:
            extra["messages"] = messages
        if prompt is not None:
            extra["prompt"] = prompt

        logger.info("LLM request", extra=extra)


def _build_prompt_breakdown(messages: list[dict[str, Any]] | None) -> dict[str, Any]:
    if not messages:
        return {}

    idx = 0
    system_content = None
    if messages and messages[0].get("role") == "system":
        system_content = messages[0].get("content")
        idx = 1

    last_user_idx = None
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "user":
            last_user_idx = i
            break

    if last_user_idx is None:
        prior_messages = messages[idx:]
        current_user_content = None
    else:
        prior_messages = messages[idx:last_user_idx]
        current_user_content = messages[last_user_idx].get("content")

    demo_pairs: list[dict[str, Any]] = []
    i = 0
    while i < len(prior_messages):
        if (
            prior_messages[i].get("role") == "user"
            and i + 1 < len(prior_messages)
            and prior_messages[i + 1].get("role") == "assistant"
        ):
            demo_pairs.append(
                {
                    "user": prior_messages[i].get("content"),
                    "assistant": prior_messages[i + 1].get("content"),
                }
            )
            i += 2
        else:
            demo_pairs = []
            break

    breakdown: dict[str, Any] = {
        "system": system_content,
        "current_user": current_user_content,
    }
    if demo_pairs:
        breakdown["demo_pairs"] = demo_pairs
    elif prior_messages:
        breakdown["demo_messages"] = prior_messages

    return breakdown
