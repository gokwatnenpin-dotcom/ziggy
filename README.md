# ziggy

A small Codex-style coding assistant that lives in your terminal.

- Kiro-style animated startup and a rich, streaming chat UI
- Reads, creates, and edits files, and can run shell commands (with your approval)
- Multi-turn conversation that keeps going until you type `/exit`
- Cross-platform: works on Windows, macOS, and Linux

## Install

Ziggy needs Windows, macOS, or Linux with Python 3.9+ available.

### Windows (PowerShell)

Clone the repo and run the installer:

```powershell
git clone https://github.com/OWNER/ziggy.git
cd ziggy
.\install.ps1
```

This creates a `ziggy` shim in `%USERPROFILE%\.local\bin` and tells you if that
directory needs to be added to your `PATH`. After that, just type:

```powershell
ziggy
```

You can also skip the installer and run the launcher in place:

```powershell
.\bin\ziggy.bat          # Command Prompt / double-click friendly
.\bin\ziggy.ps1          # PowerShell
```

If running `.ps1` scripts is blocked, either use `ziggy.bat` or allow the
script for your session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS/Linux

Clone the repo and run the installer:

```bash
git clone https://github.com/OWNER/ziggy.git
cd ziggy
./install.sh
```

Then just type:

```bash
ziggy
```

On first run ziggy sets up a private Python environment (installing `rich` and
`requests` for itself) and asks for your [OpenRouter](https://openrouter.ai/keys)
API key. Nothing is installed system-wide: everything lives in a per-user data
directory (see [Configuration](#configuration)).

To update later, `cd` into the clone and `git pull`.

### Alternative installs

If you prefer a packaged install with [pipx](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/OWNER/ziggy.git
```

or with pip:

```bash
pip install --user git+https://github.com/OWNER/ziggy.git
```

> Replace `OWNER` with the GitHub username that hosts this repo.

## Setup

On first run, ziggy asks for an [OpenRouter](https://openrouter.ai/keys) API key and
stores it in its config file:

- Windows: `%APPDATA%\ziggy\config.json`
- macOS/Linux: `~/.config/ziggy/config.json`

You can also set it via environment:

```bash
# macOS/Linux
export ZIGGY_API_KEY="sk-or-..."
```

```powershell
# Windows PowerShell
$env:ZIGGY_API_KEY = "sk-or-..."
```

## Usage

```bash
ziggy                      # start an interactive session
ziggy "what is a closure?" # ask one question, then stay interactive
```

### Commands

| Command | Description |
| --- | --- |
| `/help` | show help |
| `/clear` | start a fresh conversation |
| `/model NAME` | switch model for this session |
| `/files` | list files in the working directory |
| `/exit` | leave ziggy (also `Ctrl-D`) |

### Tools

ziggy can call these tools while it works (each is shown before it runs):

- `read_file` — read a text file
- `list_files` — list a directory
- `write_file` — create or overwrite a file
- `edit_file` — replace an exact string in a file
- `run_command` — run a shell command (asks for confirmation)

## Configuration

Settings live in the ziggy config file:

- Windows: `%APPDATA%\ziggy\config.json`
- macOS/Linux: `~/.config/ziggy/config.json`

```json
{
  "api_key": "",
  "model": "dots-studio/dots-3-note-preview:free",
  "base_url": "https://openrouter.ai/api/v1/chat/completions",
  "connect_timeout": 15,
  "read_timeout": 300,
  "max_file_chars": 40000,
  "allow_commands": true,
  "show_logo": true,
  "animate": true,
  "show_tips": true
}
```

`ZIGGY_API_KEY` overrides `api_key` when set.

## License

MIT
