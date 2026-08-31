#!/usr/bin/env bash
# Installs vscan on macOS or Linux. Run from the security-video-scanner folder:
#     bash scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

say() { printf '\n[%s] %s\n' "$1" "$2"; }

say 1 "checking python and ffmpeg"
command -v ffmpeg >/dev/null || {
  echo "    ffmpeg is missing. Install it:"
  echo "      macOS:  brew install ffmpeg"
  echo "      Ubuntu: sudo apt install -y ffmpeg"
  exit 1
}
PY=$(command -v python3 || command -v python || true)
[ -n "$PY" ] || { echo "    python3 is missing - install Python 3.10 or newer"; exit 1; }
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' || {
  echo "    Python 3.10 or newer is required (found $($PY --version))"; exit 1; }
echo "    OK  $($PY --version), ffmpeg present"

say 2 "installing vscan into .venv"
[ -d .venv ] || "$PY" -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -e ".[server,ask]"
echo "    OK"

say 3 "downloading the detection models (~140 MB, once)"
.venv/bin/vscan models fetch

cat <<'DONE'

Ready.

Check one of your videos before indexing anything:

    .venv/bin/vscan doctor "/path/to/your/video.mp4"

Or open the full web interface:

    VSCAN_FOOTAGE_DIRS=/path/to/videos VSCAN_ADMIN_PASSWORD=choose-one .venv/bin/vscan-server

DONE
