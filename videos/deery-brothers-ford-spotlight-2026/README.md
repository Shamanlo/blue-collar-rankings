# Local Vibe Check: Business Spotlight, Deery Brothers Ford, Iowa City (2026)

A 90-second spotlight and a 45-second reel built around co-owner Tyler Eads' own words
(from Deery Brothers Ford's Facebook reel): respect, transparency, in and out in 90 minutes,
no haggling. Between his soundbites: services, warranty and the Ford President's Award, Google
reviews and the call to action.

- Footage: `assets/tyler-eads-reel.mp4` (source reel, 1080x1920, with audio). Soundbites play its
  own audio (`soundbite` scenes), and captions are off for those scenes because the reel has its own.
- Facts: https://www.deeryford.com/ (services, warranty, hours, customer reviews page, 4.8★ Google rating)
- Branding: Deery blue #1A75BC, Ford blue #003478, navy #0A1A33 in `assets/theme.css`; logo `assets/deery-logo.png`
- Voice: Google Gemini TTS (gemini-3.8-flash-tts, voice Charon)

Outputs:
- `youtube.md`: titles, description (homepage link, address, phone, hours), chapters, tags, Short caption
- `out/deery-brothers-ford-spotlight-2026.mp4` (1:30) and `out/deery-brothers-ford-spotlight-2026-reel.mp4` (0:45)
- `out/thumbnail-youtube.jpg`, `out/thumbnail-reel.jpg`
- `out/deery-brothers-ford-spotlight-2026.srt`, `out/deery-brothers-ford-spotlight-2026-reel.srt`

Rebuild (from `videos/`): `P=deery-brothers-ford-spotlight-2026`, then `tts.py`, `audio.py`,
`render.mjs $P landscape`, `render.mjs $P reel`, `thumbs.mjs`, `srt.py` as in `../README.md`.
