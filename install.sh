#!/usr/bin/env bash
# Install the reverse-engineering-analysis (REA) skill for Claude Code and/or Codex.
#
#   bash install.sh             check environment, guide setup, then install (interactive)
#   bash install.sh --check     only check the environment, change nothing
#   bash install.sh --yes       accept defaults (no prompts; never runs setup commands for you)
#   bash install.sh --mode copy copy the skill instead of linking to this clone (default: link)
#   bash install.sh --uninstall remove the installed skill entries
#
# Nothing is installed until all REQUIRED checks pass.
set -uo pipefail

SKILL=reverse-engineering-analysis
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/$SKILL"
MODE=link; CHECK_ONLY=0; YES=0; UNINSTALL=0
for a in "$@"; do
  case "$a" in
    --check) CHECK_ONLY=1 ;;
    --yes|-y) YES=1 ;;
    --mode) ;; copy|link) MODE="$a" ;;
    --mode=*) MODE="${a#--mode=}" ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n 2,10p "$0"; exit 0 ;;
    *) echo "unknown option: $a"; exit 2 ;;
  esac
done

if [ -t 1 ]; then G=$'\e[32m'; Y=$'\e[33m'; R=$'\e[31m'; B=$'\e[1m'; N=$'\e[0m'; else G=; Y=; R=; B=; N=; fi
ok()   { echo "  ${G}✔${N} $*"; }
warn() { echo "  ${Y}!${N} $*"; }
bad()  { echo "  ${R}✘${N} $*"; }
hint() { echo "      → $*"; }
ask()  { [ "$YES" = 1 ] && return 1; read -r -p "      $1 [y/N] " r; [[ "$r" =~ ^[Yy] ]]; }
realdir() { python3 -c 'import os,sys;print(os.path.realpath(os.path.expanduser(sys.argv[1])))' "$1" 2>/dev/null || echo "$1"; }
vercmp_ge() { python3 -c 'import sys;a=[int(x) for x in sys.argv[1].split(".")[:3]];b=[int(x) for x in sys.argv[2].split(".")[:3]];sys.exit(0 if a>=b else 1)' "$1" "$2" 2>/dev/null; }

REQUIRED_FAIL=0
OS="$(uname -s)"

echo "${B}REA skill installer${N}  ($OS, source: $SRC)"
[ -f "$SRC/SKILL.md" ] || { bad "skill folder not found next to install.sh"; exit 1; }

# ---------------------------------------------------------------- uninstall
TARGETS=()
[ -d "$HOME/.agents/skills" ] && TARGETS+=("$HOME/.agents/skills")
[ -d "$HOME/.codex" ] && TARGETS+=("$HOME/.codex/skills")
[ -d "$HOME/.claude" ] && TARGETS+=("$HOME/.claude/skills")
if [ "$UNINSTALL" = 1 ]; then
  for t in "${TARGETS[@]}"; do
    e="$t/$SKILL"
    if [ -L "$e" ] || [ -d "$e" ]; then rm -rf "$e" && ok "removed $e"; fi
  done
  exit 0
fi

# ---------------------------------------------------------------- 1. required
echo; echo "${B}1. Required${N}"
if command -v python3 >/dev/null; then
  PV="$(python3 -c 'import platform;print(platform.python_version())')"
  if vercmp_ge "$PV" 3.9; then ok "python3 $PV (runs the skill scripts; stdlib only)"
  else bad "python3 $PV is older than 3.9"; hint "install Python 3.9+ (macOS: brew install python)"; REQUIRED_FAIL=1; fi
else
  bad "python3 not found"; hint "macOS: brew install python   ·   Ubuntu: sudo apt install python3"; REQUIRED_FAIL=1
fi

HAS_CLAUDE=0; HAS_CODEX=0
command -v claude >/dev/null || [ -d "$HOME/.claude" ] && HAS_CLAUDE=1
command -v codex  >/dev/null || [ -d "$HOME/.codex" ]  && HAS_CODEX=1
[ "$HAS_CLAUDE" = 1 ] && ok "Claude Code detected" || warn "Claude Code not detected"
[ "$HAS_CODEX" = 1 ]  && ok "Codex detected"       || warn "Codex not detected"
if [ "$HAS_CLAUDE" = 0 ] && [ "$HAS_CODEX" = 0 ]; then
  bad "need at least one agent runtime"
  hint "Claude Code: https://docs.claude.com/en/docs/claude-code   ·   Codex: npm i -g @openai/codex"
  REQUIRED_FAIL=1
fi

# ---------------------------------------------------------------- 2. browser automation (web targets)
echo; echo "${B}2. Browser automation — needed for web targets${N}"
NODE_OK=0
if command -v node >/dev/null; then
  NV="$(node -p 'process.versions.node')"
  if vercmp_ge "$NV" 20.19; then ok "node $NV (runs chrome-devtools-mcp via npx)"; NODE_OK=1
  else warn "node $NV — chrome-devtools-mcp needs 20.19+"; hint "nvm install --lts   or   brew upgrade node"; fi
else
  warn "node not found — needed for chrome-devtools-mcp"; hint "macOS: brew install node   ·   or https://nodejs.org (LTS)"
fi

CHROME=""
for c in "/Applications/Google Chrome.app" "$(command -v google-chrome 2>/dev/null)" "$(command -v google-chrome-stable 2>/dev/null)" "$(command -v chromium 2>/dev/null)"; do
  [ -n "$c" ] && [ -e "$c" ] && CHROME="$c" && break
done
[ -n "$CHROME" ] && ok "Chrome/Chromium found" || { warn "Chrome not found"; hint "install Google Chrome (chrome-devtools-mcp drives it)"; }

MCP_CMD_CLAUDE="claude mcp add chrome-devtools --scope user -- npx -y chrome-devtools-mcp@latest"
MCP_CMD_CODEX="codex mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest"
if [ "$HAS_CLAUDE" = 1 ]; then
  if grep -qi "chrome-devtools" "$HOME/.claude.json" "$HOME/.claude/settings.json" 2>/dev/null \
     || ls "$HOME/.claude/plugins/cache"/*/chrome-devtools-mcp >/dev/null 2>&1; then
    ok "Claude Code: chrome-devtools MCP configured"
  else
    warn "Claude Code: chrome-devtools MCP not configured"
    hint "$MCP_CMD_CLAUDE"
    if [ "$CHECK_ONLY" = 0 ] && [ "$NODE_OK" = 1 ] && command -v claude >/dev/null && ask "Run this command now?"; then
      $MCP_CMD_CLAUDE && ok "added (restart Claude Code to load it)"
    fi
  fi
fi
if [ "$HAS_CODEX" = 1 ]; then
  if grep -qi "chrome-devtools" "$HOME/.codex/config.toml" 2>/dev/null; then
    ok "Codex: chrome-devtools MCP configured"
  else
    warn "Codex: chrome-devtools MCP not configured"
    hint "$MCP_CMD_CODEX"
    if [ "$CHECK_ONLY" = 0 ] && [ "$NODE_OK" = 1 ] && command -v codex >/dev/null && ask "Run this command now?"; then
      $MCP_CMD_CODEX && ok "added (restart Codex to load it)"
    fi
  fi
fi

# ---------------------------------------------------------------- 3. native computer use (desktop targets)
echo; echo "${B}3. Desktop computer use — needed only for native app targets${N}"
if [ "$OS" = Darwin ]; then
  if [ -d "/Applications/Claude.app" ]; then ok "Claude desktop app present (computer use: Settings → enable Computer Use; grant Accessibility + Screen Recording)"
  else warn "Claude desktop app not found — Claude Code CLI alone has no desktop control"; hint "https://claude.ai/download"; fi
  if [ -d "$HOME/.codex/computer-use" ]; then ok "Codex Computer Use present"
  elif [ "$HAS_CODEX" = 1 ]; then warn "Codex Computer Use not found"; hint "enable the Computer Use plugin in the Codex/ChatGPT desktop app"; fi
else
  warn "desktop computer use is macOS-only in these runtimes; web targets still work"
fi

# ---------------------------------------------------------------- 4. self-test of skill scripts
echo; echo "${B}4. Self-test${N}"
TMP="$(mktemp -d)"
if python3 "$SRC/scripts/init_workspace.py" "$TMP" selftest --target http://example.test >/dev/null \
   && python3 "$SRC/scripts/log_observation.py" "$TMP/docs/reverse-engineering/selftest" --peek >/dev/null; then
  out="$(python3 "$SRC/scripts/validate_artifacts.py" "$TMP/docs/reverse-engineering/selftest" 2>&1)"; rc=$?
  if [ $rc = 1 ] && grep -q "NOT READY" <<<"$out"; then ok "scripts run and the gate blocks an empty workspace"
  else bad "validator self-test unexpected (rc=$rc)"; REQUIRED_FAIL=1; fi
else
  bad "skill scripts failed to run"; REQUIRED_FAIL=1
fi
rm -rf "$TMP"

if [ "$REQUIRED_FAIL" = 1 ]; then echo; bad "${B}Required checks failed — fix the items above and re-run.${N}"; exit 1; fi
if [ "$CHECK_ONLY" = 1 ]; then echo; ok "check finished (nothing installed)"; exit 0; fi

# ---------------------------------------------------------------- 5. install
echo; echo "${B}5. Install (mode: $MODE)${N}"
# Primary location: the cross-runtime alias if present, else the first runtime found.
PRIMARY=""
if [ -d "$HOME/.agents/skills" ]; then PRIMARY="$HOME/.agents/skills"
elif [ "$HAS_CODEX" = 1 ]; then PRIMARY="$HOME/.codex/skills"
else PRIMARY="$HOME/.claude/skills"; fi
mkdir -p "$PRIMARY"
place() { # place <dir> <source>
  local e="$1/$SKILL"
  if [ -L "$e" ] || [ -e "$e" ]; then
    if [ "$(realdir "$e")" = "$(realdir "$2")" ]; then ok "$e already installed"; return; fi
    if [ "$YES" = 1 ] || ask "$e exists — replace it?"; then rm -rf "$e"; else warn "kept existing $e"; return; fi
  fi
  if [ "$MODE" = copy ] && [ "$2" = "$SRC" ]; then cp -R "$SRC" "$e" && rm -rf "$e/__pycache__" "$e/scripts/__pycache__"
  else ln -s "$2" "$e"; fi
  ok "$e → $( [ -L "$e" ] && readlink "$e" || echo copy )"
}
place "$PRIMARY" "$SRC"
PRIMARY_REAL="$(realdir "$PRIMARY")"
for t in "$HOME/.codex/skills" "$HOME/.claude/skills"; do
  case "$t" in *".codex"*) [ "$HAS_CODEX" = 1 ] || continue ;; *".claude"*) [ "$HAS_CLAUDE" = 1 ] || continue ;; esac
  [ "$t" = "$PRIMARY" ] && continue
  mkdir -p "$t"
  [ "$(realdir "$t")" = "$PRIMARY_REAL" ] && { ok "$t is the same folder as $PRIMARY"; continue; }
  place "$t" "$PRIMARY/$SKILL"
done

echo
ok "${B}Installed.${N} Restart Claude Code / Codex, then ask:"
echo "      \"Use reverse-engineering-analysis on <url> and write the SDD/TDD plan.\""
[ "$MODE" = link ] && echo "      (linked to this clone — update with: git -C \"$HERE\" pull)"
