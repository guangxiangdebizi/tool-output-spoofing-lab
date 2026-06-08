from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


def call_chat_completion(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
    timeout_seconds: int,
    response_format: dict[str, Any] | None = None,
    retries: int = 0,
    retry_sleep_seconds: float = 1.0,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    last_error: BaseException | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_sleep_seconds)

    raise RuntimeError(f"chat completion failed after {retries + 1} attempt(s): {last_error!r}")


def response_text(response: dict[str, Any]) -> str:
    return str(response["choices"][0]["message"]["content"])
