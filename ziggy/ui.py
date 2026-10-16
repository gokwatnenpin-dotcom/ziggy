import random
import time

from rich.panel import Panel
from rich.text import Text
from rich import box

from .console import console

ZIGGY_FONT = {
    "Z": ["1111111", "0000011", "0000110", "0001100", "0011000", "1111111"],
    "I": ["1111111", "1111111", "0011100", "0011100", "1111111", "1111111"],
    "G": ["0111110", "1100000", "1011111", "1000011", "1100011", "0111110"],
    "Y": ["1100011", "0110110", "0011100", "0011100", "0011100", "0011100"],
}
GRADIENT_STOPS = [
    (0.00, (34, 211, 238)),
    (0.35, (59, 130, 246)),
    (0.70, (168, 85, 247)),
    (1.00, (236, 72, 153)),
]

TIPS = [
    "ziggy can read, create and edit files - just ask it to.",
    "run /model NAME to switch models mid-session.",
    "run_command asks you before it runs anything.",
    'pass a question as an argument: ziggy "what is a closure?"',
    "/clear wipes the conversation and frees context.",
    "config lives in ~/.config/ziggy/config.json.",
]


def build_wordmark(word="ZIGGY"):
    rows = [""] * 6
    for index, letter in enumerate(word.upper()):
        art = ZIGGY_FONT.get(letter)
        if art is None:
            continue
        if index:
            for row_index in range(6):
                rows[row_index] += " "
        for row_index in range(6):
            rows[row_index] += "".join("█" if bit == "1" else " " for bit in art[row_index])
    return rows


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient_color(fraction):
    fraction = min(1.0, max(0.0, fraction))
    for i in range(len(GRADIENT_STOPS) - 1):
        f0, c0 = GRADIENT_STOPS[i]
        f1, c1 = GRADIENT_STOPS[i + 1]
        if fraction <= f1:
            t = 0.0 if f1 == f0 else (fraction - f0) / (f1 - f0)
            return _lerp(c0, c1, t)
    return GRADIENT_STOPS[-1][1]


def render_wordmark_row(row):
    text = Text()
    span = max(1, len(row) - 1)
    for index, char in enumerate(row):
        if char == " ":
            text.append(" ")
            continue
        r, g, b = _gradient_color(index / span)
        text.append(char, style=f"bold rgb({r},{g},{b})")
    return text


def print_startup(cfg, model):
    console.print()
    if cfg.get("show_logo", True):
        rows = build_wordmark("ZIGGY")
        animate = cfg.get("animate", True) and console.is_terminal
        for row in rows:
            console.print(render_wordmark_row(row))
            if animate:
                time.sleep(0.06)
    body = Text.from_markup(
        f"[dim]model[/dim] [magenta]{model}[/magenta]\n"
        f"[dim]cwd  [/dim] [white]{_cwd()}[/white]\n"
        f"[dim]type[/dim] [white]/help[/white] [dim]for commands[/dim]"
    )
    console.print(Panel(body, border_style="cyan", box=box.ROUNDED, padding=(0, 1)))
    if cfg.get("show_tips", True):
        console.print(f" [dim]Did you know?[/dim] [white]{random.choice(TIPS)}[/white]")
    console.print()


def print_help():
    console.print(
        "[bold]commands[/bold]\n"
        "  [cyan]/help[/cyan]          show this help\n"
        "  [cyan]/clear[/cyan]         start a fresh conversation\n"
        "  [cyan]/model[/cyan] NAME    switch model for this session\n"
        "  [cyan]/files[/cyan]         list files in the working directory\n"
        "  [cyan]/exit[/cyan]          leave ziggy  [dim](also Ctrl-D)[/dim]"
    )


def _cwd():
    import os

    return os.getcwd()
