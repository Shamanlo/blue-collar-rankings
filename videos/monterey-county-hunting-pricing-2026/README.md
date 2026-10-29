# Hunting Pricing Guide, Monterey County, CA (2026): Local Vibe Check

Pricing-guide video, Short/Reel and thumbnails for the Local Vibe Check YouTube channel.
Prices come from https://indianvalleyoutfitters.com/monterey-county-hunting-price-comparison
(taken from each outfitter's website on Oct 27, 2026).

- `youtube.md`: titles, descriptions, chapters, tags and the reel caption
- `out/monterey-county-hunting-pricing-2026.mp4`: main video, 1920x1080, 3:14
- `out/monterey-county-hunting-pricing-2026-reel.mp4`: Reel/Short, 1080x1920, 0:44
- `out/thumbnail-youtube.jpg` (1280x720), `out/thumbnail-reel.jpg` (1080x1920)

## Rebuild

`script.json` holds the narration and on-screen data for both formats.

```sh
pip install edge-tts numpy
python3 tts.py                # voiceover + word timings -> out/timings.json
python3 audio.py              # music bed + voice mix -> out/{format}-mix.wav
node render.mjs landscape     # frames -> out/seg-landscape/
node render.mjs reel
node thumbs.mjs
ffmpeg -f concat -safe 0 -i out/seg-landscape/list.txt -i out/landscape-mix.wav -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/monterey-county-hunting-pricing-2026.mp4
```

`node render.mjs landscape --still 12,40` writes preview frames at those times.
