"""Generate voiceover per scene with edge-tts and record word timings.

Writes out/vo/{scene-id}.wav and out/timings.json:
  {format: [{id, start, dur, audio, words: [[t, text], ...]}]}
"""
import asyncio
import json
import os
import ssl
import subprocess
import sys
from pathlib import Path

import edge_tts
import edge_tts.communicate as ec

HERE = Path(__file__).parent
OUT = HERE / "out"
LEAD = 0.35   # silence before the first word of a scene
TAIL = 0.55   # hold after the last word

# Route through the session proxy and trust its CA when one is configured.
CA = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
if Path(CA).exists():
    ec._SSL_CTX = ssl.create_default_context(cafile=CA)
PROXY = os.environ.get("HTTPS_PROXY")


async def speak(text, voice, rate, mp3, tries=5):
    for i in range(tries):
        try:
            return await _speak(text, voice, rate, mp3)
        except Exception as e:
            print(f"  retry {i + 1}: {e}")
            await asyncio.sleep(2 * (i + 1))
    raise RuntimeError(f"TTS failed: {text[:40]}")


async def _speak(text, voice, rate, mp3):
    words = []
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary", proxy=PROXY)
    with open(mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append([chunk["offset"] / 1e7, chunk["text"]])
    return words


def duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(path)])
    return float(out)


async def main(formats):
    spec = json.loads((HERE / "script.json").read_text())
    (OUT / "vo").mkdir(parents=True, exist_ok=True)
    timings = json.loads((OUT / "timings.json").read_text()) if (OUT / "timings.json").exists() else {}
    for fmt in formats:
        t = 0.0
        scenes = []
        for s in spec[fmt]:
            mp3 = OUT / "vo" / f"{s['id']}.mp3"
            wav = OUT / "vo" / f"{s['id']}.wav"
            words = await speak(s["say"], spec["voice"], spec["rate"], mp3)
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)], check=True)
            speech = duration(wav)
            dur = round(LEAD + speech + TAIL + s.get("hold", 0), 3)
            scenes.append({"id": s["id"], "start": round(t, 3), "dur": dur, "audio": str(wav.relative_to(HERE)),
                           "words": [[round(LEAD + w, 3), txt] for w, txt in words]})
            print(f"{fmt:9} {s['id']:12} {dur:6.2f}s")
            t += dur
        timings[fmt] = scenes
        print(f"{fmt} total {t:.1f}s")
        (OUT / "timings.json").write_text(json.dumps(timings, indent=1))


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:] or ["landscape", "reel"]))
