import os
import subprocess
from pathlib import Path

from .console import console

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a text file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path, relative to the working directory or absolute."}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and folders in a directory.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Directory path (default: current directory)."}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create a new file or overwrite an existing file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write."},
                    "content": {"type": "string", "description": "Full file content."},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace an exact string in an existing file. old_string must appear exactly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to edit."},
                    "old_string": {"type": "string", "description": "Exact text to replace."},
                    "new_string": {"type": "string", "description": "Replacement text."},
                    "replace_all": {"type": "boolean", "description": "Replace every occurrence (default false)."},
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command in the working directory and return its output. The user is asked to confirm first.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "Shell command to run."}},
                "required": ["command"],
            },
        },
    },
]


def resolve_path(raw):
    path = Path(os.path.expanduser(str(raw)))
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def tool_read_file(args, cfg):
    path = resolve_path(args.get("path", ""))
    if not path.exists():
        return f"Error: no such file: {path}", "not found"
    if path.is_dir():
        return f"Error: {path} is a directory, use list_files", "is a directory"
    try:
        text = path.read_text(errors="replace")
    except Exception as exc:
        return f"Error: {exc}", "read failed"
    limit = int(cfg.get("max_file_chars", 40000))
    if len(text) > limit:
        text = text[:limit] + f"\n... [truncated at {limit} chars]"
    return text, f"read {path.name} ({len(text)} chars)"


def tool_list_files(args, cfg):
    path = resolve_path(args.get("path") or ".")
    if not path.exists():
        return f"Error: no such directory: {path}", "not found"
    if not path.is_dir():
        return f"Error: {path} is not a directory", "not a directory"
    entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    lines = []
    for entry in entries:
        suffix = "/" if entry.is_dir() else ""
        lines.append(f"{entry.name}{suffix}")
    listing = "\n".join(lines) if lines else "(empty)"
    return listing, f"{len(lines)} entries in {path}"


def tool_write_file(args, cfg):
    path = resolve_path(args.get("path", ""))
    content = args.get("content", "")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        existed = path.exists()
        path.write_text(content)
    except Exception as exc:
        return f"Error: {exc}", "write failed"
    verb = "overwrote" if existed else "created"
    return (
        f"{verb} {path} ({len(content)} chars)",
        f"{verb} {path.name} ({len(content)} chars)",
    )


def tool_edit_file(args, cfg):
    path = resolve_path(args.get("path", ""))
    old = args.get("old_string", "")
    new = args.get("new_string", "")
    replace_all = bool(args.get("replace_all", False))
    if not path.exists():
        return f"Error: no such file: {path}", "not found"
    try:
        text = path.read_text()
    except Exception as exc:
        return f"Error: {exc}", "read failed"
    count = text.count(old)
    if old == "" or count == 0:
        return "Error: old_string not found in file", "no match"
    if count > 1 and not replace_all:
        return f"Error: old_string appears {count} times, make it unique or set replace_all", "ambiguous"
    updated = text.replace(old, new) if replace_all else text.replace(old, new, 1)
    try:
        path.write_text(updated)
    except Exception as exc:
        return f"Error: {exc}", "write failed"
    replaced = count if replace_all else 1
    return f"edited {path} ({replaced} replacement(s))", f"edited {path.name}"


def tool_run_command(args, cfg):
    command = args.get("command", "")
    if not cfg.get("allow_commands", True):
        return "Error: running commands is disabled in config", "disabled"
    console.print(f"  [yellow]run:[/yellow] [white]{command}[/white]")
    try:
        answer = console.input("  [dim]allow? (y/N)[/dim] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"
    if answer not in ("y", "yes"):
        return "User denied running this command.", "denied"
    try:
        done = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=180
        )
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 180s", "timeout"
    output = (done.stdout or "") + (done.stderr or "")
    if len(output) > 20000:
        output = output[:20000] + "\n... [truncated]"
    output = output.strip() or "(no output)"
    return f"exit code {done.returncode}\n{output}", f"exit {done.returncode}"


TOOL_FUNCS = {
    "read_file": tool_read_file,
    "list_files": tool_list_files,
    "write_file": tool_write_file,
    "edit_file": tool_edit_file,
    "run_command": tool_run_command,
}


def format_args(name, args):
    parts = []
    for key, value in args.items():
        text = str(value)
        if len(text) > 40:
            text = text[:37] + "..."
        text = text.replace("\n", "\\n")
        parts.append(f"[magenta]{key}[/magenta]=[white]{text}[/white]")
    return ", ".join(parts)


def execute_tool(call, cfg):
    name = call.get("name", "")
    raw_args = call.get("arguments") or "{}"
    try:
        import json

        args = json.loads(raw_args) if raw_args.strip() else {}
    except Exception as exc:
        return f"Error: could not parse tool arguments: {exc}", "bad args"
    if not isinstance(args, dict):
        return "Error: tool arguments must be an object", "bad args"

    console.print(f"  [dim]╭─[/dim] [bold cyan]{name}[/bold cyan][dim]([/dim]{format_args(name, args)}[dim])[/dim]")
    func = TOOL_FUNCS.get(name)
    if func is None:
        result, summary = f"Error: unknown tool {name}", "unknown tool"
    else:
        try:
            result, summary = func(args, cfg)
        except Exception as exc:
            result, summary = f"Error: {exc}", "failed"
    color = "green" if not result.startswith("Error") else "red"
    console.print(f"  [dim]╰─[/dim] [{color}]{summary}[/{color}]")
    return result, summary
