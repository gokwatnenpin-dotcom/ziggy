import json
import time

import requests
from rich.live import Live
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.text import Text

from .console import console
from .tools import TOOLS, execute_tool


def stream_assistant(messages, cfg, model):
    payload = {
        "model": model,
        "messages": messages,
        "tools": TOOLS,
        "stream": True,
    }
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    timeout = (cfg.get("connect_timeout", 15), cfg.get("read_timeout", 300))

    content_parts = []
    tool_calls = {}
    last_draw = 0.0

    live = Live(
        Spinner("dots", text=Text(" thinking", style="dim")),
        console=console,
        refresh_per_second=12,
        transient=False,
        vertical_overflow="visible",
    )
    live.start()
    try:
        response = requests.post(
            cfg["base_url"], headers=headers, json=payload, stream=True, timeout=timeout
        )
        if response.status_code != 200:
            try:
                message = response.json().get("error", {}).get("message", response.text)
            except Exception:
                message = response.text
            raise RuntimeError(f"API error {response.status_code}: {message}")

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data:"):
                data = line[5:].strip()
            else:
                continue
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
            except Exception:
                continue
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}

            piece = delta.get("content")
            if piece:
                content_parts.append(piece)
                now = time.time()
                if now - last_draw > 0.05:
                    live.update(Markdown("".join(content_parts)))
                    last_draw = now

            for raw_call in delta.get("tool_calls") or []:
                index = raw_call.get("index", 0)
                slot = tool_calls.setdefault(index, {"id": "", "name": "", "arguments": ""})
                if raw_call.get("id"):
                    slot["id"] = raw_call["id"]
                function = raw_call.get("function") or {}
                if function.get("name"):
                    slot["name"] = function["name"]
                if function.get("arguments"):
                    slot["arguments"] += function["arguments"]
    finally:
        if content_parts:
            live.update(Markdown("".join(content_parts)))
        live.stop()

    ordered = [tool_calls[key] for key in sorted(tool_calls)]
    for index, call in enumerate(ordered):
        if not call["id"]:
            call["id"] = f"call_{index}"
    return "".join(content_parts), ordered


def run_turn(messages, cfg, model):
    while True:
        content, calls = stream_assistant(messages, cfg, model)
        assistant = {"role": "assistant", "content": content or None}
        if calls:
            assistant["tool_calls"] = [
                {
                    "id": call["id"],
                    "type": "function",
                    "function": {"name": call["name"], "arguments": call["arguments"]},
                }
                for call in calls
            ]
        messages.append(assistant)
        if not calls:
            return
        for call in calls:
            result, _ = execute_tool(call, cfg)
            messages.append(
                {"role": "tool", "tool_call_id": call["id"], "content": result}
            )
