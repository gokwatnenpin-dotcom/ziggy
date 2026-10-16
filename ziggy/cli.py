import os
import sys

import requests

from . import config
from .agent import run_turn
from .console import console
from .tools import tool_list_files
from .ui import print_help, print_startup

SYSTEM_PROMPT = (
    "You are ziggy, a coding assistant running in the user's terminal. "
    "You can read, list, create and edit files, and run shell commands using the provided tools. "
    "Always use the tools instead of guessing file contents. "
    "Prefer edit_file for small changes and write_file for new files. "
    "Keep answers concise and use markdown. Working directory: {cwd}"
)


def handle_slash(command, messages, model, cfg):
    parts = command.split(maxsplit=1)
    name = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if name in ("/exit", "/quit", "/q"):
        return messages, model, True
    if name == "/help":
        print_help()
    elif name == "/clear":
        messages = messages[:1]
        console.print("[dim]conversation cleared[/dim]")
    elif name == "/model":
        if arg:
            model = arg
            console.print(f"[dim]model set to[/dim] [magenta]{model}[/magenta]")
        else:
            console.print(f"[dim]current model:[/dim] [magenta]{model}[/magenta]")
    elif name == "/files":
        listing, summary = tool_list_files({"path": "."}, cfg)
        console.print(summary)
        console.print(listing)
    else:
        console.print(f"[red]unknown command:[/red] {name}  [dim]/help[/dim]")
    return messages, model, False


def main():
    cfg = config.load()
    config.ensure_api_key(cfg)
    model = cfg["model"]
    print_startup(cfg, model)
    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(cwd=os.getcwd())}]

    pending = " ".join(sys.argv[1:]).strip()

    while True:
        if pending:
            question = pending
            pending = ""
            console.print(f"[bold cyan]›[/bold cyan] {question}")
        else:
            try:
                question = console.input("\n[bold cyan]›[/bold cyan] ")
            except (EOFError, KeyboardInterrupt):
                console.print()
                break
            question = question.strip()

        if not question:
            continue
        if question.startswith("/"):
            messages, model, should_exit = handle_slash(question, messages, model, cfg)
            if should_exit:
                break
            continue

        messages.append({"role": "user", "content": question})
        try:
            run_turn(messages, cfg, model)
        except KeyboardInterrupt:
            console.print("\n[yellow]cancelled[/yellow]")
        except requests.exceptions.Timeout:
            console.print("[red]request timed out[/red]")
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
        except requests.exceptions.RequestException as exc:
            console.print(f"[red]network error: {exc}[/red]")

    console.print("[dim]bye[/dim]")
