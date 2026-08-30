#!/usr/bin/env bash
# One command: Converge dashboard -> finished vertical MP4.
#
#   ./render.sh                       # today's dashboard from the repo root
#   ./render.sh --source path.html    # any dashboard HTML
#   ./render.sh --payload feed.json   # skip extraction, render a payload directly
#   ./render.sh --fps 60 --crf 21
#
# Exit codes: non-zero if the render was not reproducible (network touched,
# clock read, font missing). A wrong video is worse than no video.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$HERE/../../index.html"
PAYLOAD=""
OUT=""
EXTRA=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source)  SOURCE="$2"; shift 2 ;;
    --payload) PAYLOAD="$2"; shift 2 ;;
    --out|-o)  OUT="$2"; shift 2 ;;
    *)         EXTRA+=("$1"); shift ;;
  esac
done

mkdir -p "$HERE/out" "$HERE/payload"

if [[ -z "$PAYLOAD" ]]; then
  PAYLOAD="$HERE/payload/converge.json"
  echo "[1/2] extracting feed  <- $SOURCE"
  python3 "$HERE/scripts/extract_feed.py" "$SOURCE" -o "$PAYLOAD"
else
  echo "[1/2] using payload    <- $PAYLOAD"
fi

DATE="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["date"])' "$PAYLOAD")"
[[ -z "$OUT" ]] && OUT="$HERE/out/converge-$DATE.mp4"

echo "[2/2] rendering        -> $OUT"
python3 "$HERE/scripts/capture.py" "$PAYLOAD" \
  --out "$OUT" \
  --manifest "$HERE/out/$(basename "${OUT%.mp4}").manifest.json" \
  ${EXTRA[@]+"${EXTRA[@]}"}

echo
echo "done: $OUT"
