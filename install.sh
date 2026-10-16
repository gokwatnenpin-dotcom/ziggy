#!/usr/bin/env bash
# Installs the `ziggy` command. Works from a clone or via: curl ... | bash
set -euo pipefail

REPO_URL="${ZIGGY_REPO:-https://github.com/OWNER/ziggy.git}"
ZIGGY_HOME="${ZIGGY_HOME:-$HOME/.local/share/ziggy}"
BIN_DIR="${ZIGGY_BIN_DIR:-$HOME/.local/bin}"

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" >/dev/null 2>&1 && pwd)"

if [ -f "$SELF_DIR/pyproject.toml" ] && [ -d "$SELF_DIR/ziggy" ]; then
    SRC="$SELF_DIR"
else
    SRC="$ZIGGY_HOME/src"
    if [ ! -d "$SRC/.git" ]; then
        echo "Cloning ziggy into $SRC ..."
        mkdir -p "$ZIGGY_HOME"
        git clone --depth 1 "$REPO_URL" "$SRC"
    fi
fi

chmod +x "$SRC/bin/ziggy" 2>/dev/null || true
mkdir -p "$BIN_DIR"
ln -sf "$SRC/bin/ziggy" "$BIN_DIR/ziggy"
echo "Installed: $BIN_DIR/ziggy"

add_path() {
    local rc="$1"
    [ -f "$rc" ] || return 0
    if grep -q 'ziggy path' "$rc" 2>/dev/null; then
        return 0
    fi
    printf '\n# ziggy path\nexport PATH="%s:$PATH"\n' "$BIN_DIR" >> "$rc"
    echo "Added $BIN_DIR to PATH in $rc"
}

case ":${PATH}:" in
    *":$BIN_DIR:"*)
        ;;
    *)
        add_path "$HOME/.bashrc"
        add_path "$HOME/.zshrc"
        echo "Restart your terminal (or run: export PATH=\"$BIN_DIR:\$PATH\")."
        ;;
esac

echo
echo "Done. Type 'ziggy' to start - it finishes setup on first run."
