# Local Vibe Check videos

Pricing-guide videos for the Local Vibe Check YouTube channel. Each folder is one video:
`script.json` (narration + on-screen data for the 16:9 video and the 9:16 Reel/Short),
`assets/` (photos and logos), `youtube.md` (titles, descriptions, chapters, tags) and the
finished files in `out/`.

`_engine/` holds the shared renderer, voiceover, music and thumbnail scripts plus the
brand fonts and pin logo.

## Build a video

Needs Python 3 with `edge-tts` and `numpy`, Node with Playwright + Chromium, and ffmpeg.

Voice: by default the Microsoft neural voice set by `"voice"`/`"rate"` in `script.json`.
For Google Gemini TTS, set `"tts": "gemini"` and `"gemini": {"model": "gemini-3.8-flash-tts",
"voice": "Charon"}`, provide `GEMINI_API_KEY` as an environment secret (never commit it), and
`pip install faster-whisper` (a local Whisper model times the captions against Gemini's audio and
flags any take that doesn't match the script). A scene's optional `"speak"` text is what
Gemini reads (e.g. numbers spelled out) while `"say"` stays the caption text.
Run from this folder, with `P` set to the project folder:

```sh
python3 _engine/tts.py $P                  # voiceover + word timings -> out/timings.json
python3 _engine/audio.py $P                # music bed + voice mix -> out/{format}-mix.wav
node _engine/render.mjs $P landscape       # frames + mux -> out/$P.mp4
node _engine/render.mjs $P reel            # -> out/$P-reel.mp4
node _engine/thumbs.mjs $P                 # out/thumbnail-youtube.jpg, out/thumbnail-reel.jpg
```

`node _engine/render.mjs $P landscape --still 12,40` writes preview frames at those times.
`tts.py` caches each scene's take, so only edited lines are re-recorded.

## Scene kinds

`title`, `define`, `list`, `bars`, `ranges`, `price`, `mini`, `stats`, `deposit`, `table`, `reviews`,
`factors`, `steps`, `quote`, `winner`, `hunts`, `cta`. See the two existing `script.json`
files for the fields each one takes. `data-cue`-style fields (`cue`, `priceCue`, `urlCue`,
`nameCue`) time an element to the first spoken word that starts with that text.
