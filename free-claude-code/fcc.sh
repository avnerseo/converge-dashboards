#!/usr/bin/env bash
# Free Claude Code (FCC) — isolated launcher for macOS / Linux / WSL.
#
# Runs the FCC proxy (https://github.com/Alishahryar1/free-claude-code) and points
# a SEPARATE Claude Code profile at it. Your existing ~/.claude install, login and
# settings are never touched: everything lives under $FCC_HOME and the proxied
# Claude Code runs with its own CLAUDE_CONFIG_DIR.
#
# Usage: ./fcc.sh setup | start | claude | status | stop | uninstall

set -euo pipefail

FCC_HOME="${FCC_HOME:-$HOME/.free-claude-code}"
FCC_PORT="${FCC_PORT:-8082}"
APP_DIR="$FCC_HOME/app"
ENV_FILE="$APP_DIR/.env"
CONFIG_DIR="$FCC_HOME/claude-config"
LOG_FILE="$FCC_HOME/server.log"
PID_FILE="$FCC_HOME/server.pid"
REPO_URL="https://github.com/Alishahryar1/free-claude-code.git"

die()  { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33mwarn:\033[0m %s\n' "$*" >&2; }

have() { command -v "$1" >/dev/null 2>&1; }

ensure_uv() {
  if have uv; then return; fi
  if [ -x "$HOME/.local/bin/uv" ]; then export PATH="$HOME/.local/bin:$PATH"; return; fi
  die "uv is not installed. Install it first (see README, step 1) and re-run."
}

port_open() {
  (exec 3<>"/dev/tcp/127.0.0.1/$FCC_PORT") >/dev/null 2>&1 && exec 3>&- && return 0
  return 1
}

cmd_setup() {
  have git  || die "git is required"
  have curl || die "curl is required"
  have claude || warn "the 'claude' CLI was not found on PATH — install Claude Code before using './fcc.sh claude'"
  ensure_uv

  mkdir -p "$FCC_HOME" "$CONFIG_DIR"
  chmod 700 "$FCC_HOME"

  if [ -d "$APP_DIR/.git" ]; then
    info "updating existing checkout in $APP_DIR"
    git -C "$APP_DIR" pull --ff-only
  else
    info "cloning FCC into $APP_DIR"
    git clone --depth 1 "$REPO_URL" "$APP_DIR"
  fi

  info "resolving python dependencies (uv sync)"
  (cd "$APP_DIR" && uv sync)

  if [ -f "$ENV_FILE" ]; then
    info ".env already exists — leaving it as is (edit $ENV_FILE to change provider)"
  else
    if [ -f "$APP_DIR/.env.example" ]; then cp "$APP_DIR/.env.example" "$ENV_FILE"; else : > "$ENV_FILE"; fi
    chmod 600 "$ENV_FILE"
    echo
    echo "Which provider should the proxy use?"
    echo "  1) OpenRouter   (recommended: you can opt out of training in account settings)"
    echo "  2) NVIDIA NIM   (bigger free quota, but free-tier inputs are used for training)"
    echo "  3) Local only   (LM Studio / Ollama — nothing leaves your machine)"
    printf 'choice [1]: '; read -r choice
    case "${choice:-1}" in
      2) key_var=NVIDIA_NIM_API_KEY ;;
      3) key_var="" ;;
      *) key_var=OPENROUTER_API_KEY ;;
    esac
    if [ -n "$key_var" ]; then
      printf '%s (input hidden): ' "$key_var"; read -rs api_key; echo
      [ -n "$api_key" ] || die "no key entered"
      # replace an existing line if .env.example already defines it, else append
      if grep -q "^${key_var}=" "$ENV_FILE" 2>/dev/null; then
        tmp=$(mktemp); grep -v "^${key_var}=" "$ENV_FILE" > "$tmp"; mv "$tmp" "$ENV_FILE"
      fi
      printf '%s=%s\n' "$key_var" "$api_key" >> "$ENV_FILE"
      chmod 600 "$ENV_FILE"
      info "wrote $key_var to $ENV_FILE (mode 600)"
    else
      info "no cloud key stored — configure your local endpoint in the admin UI"
    fi
  fi

  echo
  info "setup complete."
  echo "    next:  ./fcc.sh start     # boot the proxy"
  echo "           ./fcc.sh claude    # open Claude Code against it"
}

cmd_start() {
  [ -d "$APP_DIR" ] || die "not set up yet — run './fcc.sh setup' first"
  if port_open; then info "proxy already listening on port $FCC_PORT"; return; fi
  ensure_uv
  info "starting fcc-server on port $FCC_PORT (log: $LOG_FILE)"
  ( cd "$APP_DIR" && nohup uv run fcc-server >"$LOG_FILE" 2>&1 & echo $! > "$PID_FILE" )
  for _ in $(seq 1 40); do
    if port_open; then
      info "proxy is up   ->  admin UI: http://127.0.0.1:$FCC_PORT"
      echo "    pick your model there, then run: ./fcc.sh claude"
      return
    fi
    sleep 0.5
  done
  warn "server did not open port $FCC_PORT within 20s — last log lines:"
  tail -n 25 "$LOG_FILE" >&2 || true
  exit 1
}

cmd_claude() {
  have claude || die "the 'claude' CLI is not installed"
  port_open || die "proxy is not running — run './fcc.sh start' first"
  info "launching Claude Code against the local proxy (isolated profile: $CONFIG_DIR)"
  mkdir -p "$CONFIG_DIR"
  # These three vars are the whole trick: a separate config dir keeps your paid
  # login untouched, and the base URL sends traffic to the local proxy instead.
  env CLAUDE_CONFIG_DIR="$CONFIG_DIR" \
      ANTHROPIC_BASE_URL="http://127.0.0.1:$FCC_PORT" \
      ANTHROPIC_AUTH_TOKEN="freecc" \
      claude "$@"
}

cmd_status() {
  echo "FCC_HOME : $FCC_HOME"
  echo "app      : $([ -d "$APP_DIR" ] && echo present || echo 'missing (run setup)')"
  echo "env file : $([ -f "$ENV_FILE" ] && echo "$ENV_FILE" || echo 'missing')"
  echo "port     : $FCC_PORT $(port_open && echo '(listening)' || echo '(closed)')"
  [ -f "$PID_FILE" ] && echo "pid      : $(cat "$PID_FILE")"
  echo "profile  : $CONFIG_DIR   # proxied Claude Code config, separate from ~/.claude"
}

cmd_stop() {
  if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    pid=$(cat "$PID_FILE")
    kill "$pid" && info "stopped pid $pid"
    rm -f "$PID_FILE"
  else
    warn "no running server recorded in $PID_FILE"
  fi
}

cmd_uninstall() {
  cmd_stop || true
  printf 'delete %s and everything in it? [y/N]: ' "$FCC_HOME"; read -r a
  case "$a" in
    [yY]*) rm -rf "$FCC_HOME"; info "removed $FCC_HOME — your ~/.claude was never modified" ;;
    *)     info "cancelled" ;;
  esac
}

case "${1:-}" in
  setup)     cmd_setup ;;
  start)     cmd_start ;;
  claude)    shift; cmd_claude "$@" ;;
  status)    cmd_status ;;
  stop)      cmd_stop ;;
  uninstall) cmd_uninstall ;;
  *) echo "usage: $0 {setup|start|claude|status|stop|uninstall}" >&2; exit 2 ;;
esac
