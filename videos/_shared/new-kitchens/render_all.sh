#!/usr/bin/env bash
# Voice and render every New Kitchens city video. Run from videos/:
#   bash _shared/new-kitchens/render_all.sh
# Voiceovers are recorded one city at a time; each city renders as soon as its voiceover is done.
set -u
cd "$(dirname "$0")/../.."
CITIES=$(ls -d new-kitchens-*-2026 | sort)
(
  for P in $CITIES; do
    rm -f "$P/out/tts.done"
    python3 -u _engine/tts.py "$P" > "$P/out/tts.log" 2>&1 && touch "$P/out/tts.done" || touch "$P/out/tts.failed"
  done
) &
for P in $CITIES; do
  until [ -e "$P/out/tts.done" ] || [ -e "$P/out/tts.failed" ]; do sleep 5; done
  if [ -e "$P/out/tts.failed" ]; then echo "$P: TTS FAILED"; continue; fi
  python3 _engine/audio.py "$P" > "$P/out/render.log" 2>&1 &&
    node _engine/render.mjs "$P" landscape --workers 5 >> "$P/out/render.log" 2>&1 &&
    node _engine/render.mjs "$P" reel --workers 5 >> "$P/out/render.log" 2>&1 &&
    node _engine/thumbs.mjs "$P" >> "$P/out/render.log" 2>&1 &&
    echo "$P: done $(date +%H:%M)" || echo "$P: RENDER FAILED"
done
wait
echo ALL DONE
