#!/usr/bin/env bash
# SVG -> PNG przez chromium. Uruchamiaj z katalogu research/figury.
set -euo pipefail
cd "$(dirname "$0")"

for name in honeycomb labirynt mapa roza; do
    python3 "$name.py"
    wrapper="$(mktemp --suffix=.html)"
    cat > "$wrapper" <<EOF
<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body { margin: 0; width: 100%; height: 100%; background: #fff; }
  img { width: 100vw; height: 100vh; object-fit: contain; display: block; }
</style></head>
<body><img src="file://$PWD/$name.svg"></body></html>
EOF
    chromium --headless --disable-gpu --no-sandbox --hide-scrollbars \
        --window-size=1600,1600 --screenshot="$PWD/$name.png" \
        "file://$wrapper" 2>/dev/null
    rm -f "$wrapper"
done

echo "PNG: honeycomb.png labirynt.png mapa.png roza.png"
