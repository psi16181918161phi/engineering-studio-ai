"""WHAT: Thin HTTP client for Fireworks AI chat-completions, with a local
llama.cpp fallback endpoint, so no single provider is hard-coded.
WHY: AMD LabLabAI Hackathon Act II provisions Fireworks AI access; the
Model Routing Layer pattern (VISION_MULTIMODAL_DEPLOYABLE_AGENTS_CLEAN.md
Section 12.3) requires any agent to be swappable to a different backend
by config alone, never a code change.
HOW: A single `ModelClient` class exposes `complete(system, user) -> str`.
Construction reads model/base-url/api-key from environment variables
(see .env.example); raises `ModelUnavailableError` on failure rather than
fabricating a response (live-data honesty rule, AGENTS.md §5).
"""

from __future__ import annotations

import os

import requests

from engineering_studio.exceptions import ModelUnavailableError

__all__ = ["ModelClient", "ModelUnavailableError"]


class ModelClient:
    """WHAT: Minimal chat-completions client routed to Fireworks AI by default.

    ATTRIBUTES:
        base_url (str): Inference endpoint root, from FIREWORKS_BASE_URL.
        api_key (str): Bearer token, from FIREWORKS_API_KEY. Never logged.
        model (str): Fully-qualified model id, e.g.
            "accounts/fireworks/models/llama-v3p1-70b-instruct".
        timeout_s (float): Per-request timeout in seconds.

    WHY: One class, one responsibility (SRP) — issuing a single chat
    completion request and returning plain text. Retry/backoff and model
    selection strategy live in the orchestrator, not here.

    HOW: `complete()` posts an OpenAI-compatible chat payload; raises
    `ModelUnavailableError` on any non-2xx response or network exception.
    Thread-safety: stateless after construction; safe to share across
    concurrently dispatched specialist calls.
    """

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_s: float = 60.0,
        max_tokens: int = 1024,
        reasoning_effort: str | None = "low",
    ) -> None:
        resolved_base_url = (
            base_url if base_url is not None else os.environ.get("FIREWORKS_BASE_URL", "")
        )
        self.base_url = resolved_base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("FIREWORKS_API_KEY", "")
        self.model = model
        self.timeout_s = timeout_s
        # WHAT: Caps visible+hidden-reasoning output and reasoning depth.
        # WHY: Fireworks reasoning models (GLM-5.x, Kimi-K2.x, DeepSeek-V4,
        # GPT-OSS Harmony) emit hidden reasoning tokens before the visible
        # answer, ON by default on most of them. A non-streaming request
        # with neither cap blocks until that full hidden trace finishes —
        # the observed "hangs / times out on a random stage" symptom.
        # Fireworks also rejects non-streaming requests with max_tokens
        # over 4096, so keep this at or below that.
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort
        if not self.base_url:
            raise ValueError("FIREWORKS_BASE_URL is not set (see .env.example).")

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """WHAT: Sends one chat-completion request and returns the reply text.

        ARGS:
            system_prompt (str): The Task Specification / scope contract.
            user_prompt (str): The product brief or upstream artifact content.

        RETURNS:
            str: The model's response text.

        RAISES:
            ModelUnavailableError: On network failure, timeout, or non-2xx
                HTTP status. Never returns a fabricated placeholder.
        """
        if not self.api_key:
            raise ModelUnavailableError(
                "FIREWORKS_API_KEY is not set — refusing to call a paid API "
                "without credentials (see .env.example)."
            )
        payload: dict[str, object] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": self.max_tokens,
        }
        # WHAT: Only sent when set — the local llama.cpp fallback endpoint
        # does not understand this Fireworks-specific parameter, and some
        # models (Harmony/GPT-OSS) error on unsupported values like "none".
        if self.reasoning_effort is not None:
            payload["reasoning_effort"] = self.reasoning_effort
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=self.timeout_s,
            )
        except requests.RequestException as exc:
            raise ModelUnavailableError(f"network error calling {self.model}: {exc}") from exc

        if response.status_code != 200:
            raise ModelUnavailableError(
                f"{self.model} returned HTTP {response.status_code}: {response.text[:300]}"
            )

        response_payload = response.json()
        try:
            return str(response_payload["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelUnavailableError(
                f"unexpected response shape from {self.model}: {response_payload!r}"
            ) from exc