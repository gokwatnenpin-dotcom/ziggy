import json
import os
import sys
from pathlib import Path

from rich.prompt import Prompt

CONFIG_DIR = Path.home() / ".config" / "ziggy"
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULTS = {
    "api_key": "",
    "model": "dots-studio/dots-3-note-preview:free",
    "base_url": "https://openrouter.ai/api/v1/chat/completions",
    "connect_timeout": 15,
    "read_timeout": 300,
    "max_file_chars": 40000,
    "allow_commands": True,
    "show_logo": True,
    "animate": True,
    "show_tips": True,
}


def load():
    cfg = DEFAULTS.copy()
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
        except Exception as exc:
            print(f"Could not parse {CONFIG_PATH}: {exc}", file=sys.stderr)
            sys.exit(1)
        if isinstance(data, dict):
            cfg.update(data)
    else:
        save(cfg)
    return cfg


def save(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")


def ensure_api_key(cfg):
    env_key = os.environ.get("ZIGGY_API_KEY", "").strip()
    if env_key:
        cfg["api_key"] = env_key
        return
    if cfg.get("api_key", "").strip():
        return
    print("ziggy needs an OpenRouter API key to work.")
    print("Create one at https://openrouter.ai/keys then paste it below.\n")
    if sys.stdin.isatty():
        key = Prompt.ask("API key", password=True).strip()
    else:
        key = sys.stdin.readline().strip()
    if not key:
        print("No key entered. Exiting.", file=sys.stderr)
        sys.exit(1)
    cfg["api_key"] = key
    save(cfg)
    print(f"\nSaved to {CONFIG_PATH}\n")
