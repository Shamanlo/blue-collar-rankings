"""Generate voiceover per scene and record word timings.

    python3 _engine/tts.py <project> [landscape] [reel]

Voice comes from script.json. Default is Microsoft neural TTS via edge-tts ("voice", "rate").
With "tts": "gemini" it uses Google Gemini TTS ("gemini": {"model", "voice", "style", "speed"})
and the GEMINI_API_KEY env var (or ~/.gemini_key); Gemini returns no word timings, so a
local Whisper model times the script's words against the audio.

Writes {project}/out/vo/{scene-id}.wav and {project}/out/timings.json:
  {format: [{id, start, dur, audio, words: [[t, text], ...]}]}
"""
import asyncio
import base64
import difflib
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import edge_tts
import edge_tts.communicate as ec

HERE = Path(sys.argv[1]).resolve()
OUT = HERE / "out"
LEAD = 0.35   # silence before the first word of a scene
TAIL = 0.55   # hold after the last word

# Route through the session proxy and trust its CA when one is configured.
CA = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
if Path(CA).exists():
    ec._SSL_CTX = ssl.create_default_context(cafile=CA)
PROXY = os.environ.get("HTTPS_PROXY")


async def speak(text, voice, rate, mp3, tries=8):
    # Reuse the last take when the line, voice and rate haven't changed.
    cache = mp3.with_suffix(".json")
    key = {"text": text, "voice": voice, "rate": rate}
    if cache.exists() and mp3.exists():
        saved = json.loads(cache.read_text())
        if saved["key"] == key:
            return saved["words"]
    for i in range(tries):
        try:
            words = await _speak(text, voice, rate, mp3)
            cache.write_text(json.dumps({"key": key, "words": words}))
            return words
        except Exception as e:
            print(f"  retry {i + 1}: {e}")
            await asyncio.sleep(3 * (i + 1))
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


def gemini_key():
    key = os.environ.get("GEMINI_API_KEY")
    path = Path.home() / ".gemini_key"
    if not key and path.exists():
        key = path.read_text().strip()
    if not key:
        raise SystemExit("Set GEMINI_API_KEY (or ~/.gemini_key) to use Gemini TTS.")
    return key


def gemini_audio(text, cfg, out_wav, tries=6):
    prompt = f"{cfg['style']}: {text}" if cfg.get("style") else text
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": cfg["voice"]}}}}}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{cfg['model']}:generateContent"
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "x-goog-api-key": gemini_key()})
            r = json.load(urllib.request.urlopen(req, timeout=180))
            data = base64.b64decode(r["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            raw = out_wav.with_suffix(".gemini.wav")
            raw.write_bytes(data)
            # Trim silence at both ends so LEAD/TAIL stay consistent, then speed up if asked.
            filters = ["silenceremove=start_periods=1:start_threshold=-45dB",
                       "areverse", "silenceremove=start_periods=1:start_threshold=-45dB", "areverse"]
            if cfg.get("speed", 1) != 1:
                filters.append(f"atempo={cfg['speed']}")
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw), "-af", ",".join(filters),
                            "-ar", "48000", "-ac", "1", str(out_wav)], check=True)
            return
        except (urllib.error.URLError, KeyError, IndexError, TimeoutError) as e:
            detail = e.read()[:200] if isinstance(e, urllib.error.HTTPError) else e
            print(f"  retry {i + 1}: {detail}")
            time.sleep(4 * (i + 1))
    raise RuntimeError(f"Gemini TTS failed: {text[:40]}")


_whisper = None


def whisper_words(wav):
    global _whisper
    import numpy as np
    from faster_whisper import WhisperModel
    if _whisper is None:
        _whisper = WhisperModel("base.en", device="cpu", compute_type="int8")
    pcm = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", str(wav), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"])
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, _ = _whisper.transcribe(audio, word_timestamps=True, language="en")
    return [(w.start, w.word.strip()) for seg in segs for w in seg.words]


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def align(say, heard):
    """Give each script word the time Whisper heard it; interpolate the ones it missed."""
    tokens = [re.sub(r'^["“”]+|["“”.,?!:;]+$', "", t) for t in say.split()]
    tokens = [t for t in tokens if t]
    sm = difflib.SequenceMatcher(a=[norm(t) for t in tokens], b=[norm(w) for _, w in heard], autojunk=False)
    times = [None] * len(tokens)
    for a0, b0, n in sm.get_matching_blocks():
        for k in range(n):
            times[a0 + k] = heard[b0 + k][0]
    known = [i for i, t in enumerate(times) if t is not None]
    end = heard[-1][0] if heard else 0
    for i, t in enumerate(times):
        if t is None:
            prev = max([k for k in known if k < i], default=None)
            nxt = min([k for k in known if k > i], default=None)
            t0 = times[prev] if prev is not None else 0
            t1 = times[nxt] if nxt is not None else end
            i0 = prev if prev is not None else -1
            i1 = nxt if nxt is not None else len(tokens)
            times[i] = t0 + (t1 - t0) * (i - i0) / (i1 - i0)
    # Score the take on characters, so "$45,000" vs Whisper's "45 ,000" isn't a mismatch.
    ratio = difflib.SequenceMatcher(a=norm(say), b=norm("".join(w for _, w in heard)), autojunk=False).ratio()
    return [[round(t, 3), w] for t, w in zip(times, tokens)], ratio, " ".join(w for _, w in heard)


def speak_gemini(say, text, cfg, wav):
    # "text" is what Gemini reads (a scene's optional "speak", e.g. numbers spelled out);
    # "say" is what the captions show.
    cache = wav.with_suffix(".json")
    key = {"text": text, "tts": "gemini", **cfg}
    if cache.exists() and wav.exists():
        saved = json.loads(cache.read_text())
        if saved["key"] == key:
            return saved["words"]
    gemini_audio(text, cfg, wav)
    words, ratio, heard = align(say, whisper_words(wav))
    if ratio < 0.85:
        print(f"  check this take ({ratio:.0%} match). Heard: {heard}")
    cache.write_text(json.dumps({"key": key, "words": words, "match": round(ratio, 3)}))
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
            if spec.get("tts") == "gemini":
                words = speak_gemini(s["say"], s.get("speak", s["say"]), spec["gemini"], wav)
            else:
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
    asyncio.run(main(sys.argv[2:] or ["landscape", "reel"]))
