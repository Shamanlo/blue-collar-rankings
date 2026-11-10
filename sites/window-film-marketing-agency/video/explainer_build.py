#!/usr/bin/env python3
"""Builds the explainer videos defined in explainers.py.

    GEMINI_API_KEY=... python3 video/explainer_build.py <root> [slug ...]

For each video, <root>/<slug>/ gets the voiceover (vo/, Gemini TTS, cached by text), and
plan-wide.json (16:9 video) and plan-reel.json (9:16 Short), in the same format as five_build.py:
explainer.html draws a plan, five_audio.py mixes it, render.mjs renders it. It also writes
<root>/<slug>/chapters.json (YouTube chapters for the long video).
<root>/<slug>/img should link to the shared screenshots folder.
"""
import base64
import difflib
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from explainers import VIDEOS  # noqa: E402

ROOT = os.path.abspath(sys.argv[1])
ONLY = sys.argv[2:]
MODEL = "gemini-3.8-flash-tts"
VOICE = "Orus"
STYLE = "Confident, upbeat and direct, like a sharp marketing coach talking to contractors. Brisk, natural pace with clear diction."
GRID = 0.5
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
snap = lambda t: math.ceil(t / GRID - 1e-6) * GRID
_whisper = None


# ---------- voice ----------
def tts(text):
    body = {"model": MODEL,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text, "annotations": [{"type": "speech_metadata", "style": STYLE}]}]}],
            "response_format": {"type": "audio"}, "generation_config": {"speech_config": [{"voice": VOICE}]}}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=json.dumps(body).encode(),
                                 headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                j = json.load(r)
            break
        except urllib.error.HTTPError as err:
            if err.code not in (429, 500, 503) or attempt == 7:
                raise
            wait = int(err.headers.get("Retry-After") or 0) or 20 * (attempt + 1)
            print(f"  rate limited ({err.code}), waiting {wait} s")
            time.sleep(wait)
    for step in j["steps"]:
        for c in step.get("content", []):
            if c.get("type") == "audio":
                return base64.b64decode(c["data"])
    raise RuntimeError("no audio in response")


def speak(vo_dir, text):
    """Returns (id, duration, words) for a line, generating and transcribing it once."""
    os.makedirs(vo_dir, exist_ok=True)
    lid = "v" + hashlib.sha1(f"{MODEL}|{VOICE}|{STYLE}|{text}".encode()).hexdigest()[:12]
    wav, meta_path = os.path.join(vo_dir, lid + ".wav"), os.path.join(vo_dir, lid + ".json")
    if os.path.exists(meta_path):
        m = json.load(open(meta_path))
        return lid, m["dur"], m["words"]
    raw = os.path.join(vo_dir, lid + ".raw.wav")
    open(raw, "wb").write(tts(text))
    sr, x = wavfile.read(raw)
    x = x.astype(np.float32) / 32768.0
    if x.ndim > 1:
        x = x.mean(axis=1)
    loud = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
    x = x[max(0, loud[0] - int(0.03 * sr)): min(len(x), loud[-1] + int(0.12 * sr))]
    x *= 10 ** (-20 / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-9)
    x = np.tanh(x * 1.2) / 1.2
    wavfile.write(wav, sr, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("small.en", device="cpu", compute_type="int8")
    x16 = np.interp(np.arange(0, len(x), sr / 16000), np.arange(len(x)), x).astype(np.float32)
    segs, _ = _whisper.transcribe(x16, word_timestamps=True, beam_size=5)
    words = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words]
    ratio = difflib.SequenceMatcher(None, [norm(w) for w in text.split()], [norm(w[2]) for w in words]).ratio()
    print(f"  spoke {len(x) / sr:4.1f} s, match {ratio:.2f}: {' '.join(w[2] for w in words)}")
    json.dump({"text": text, "dur": round(len(x) / sr, 3), "words": words}, open(meta_path, "w"))
    os.remove(raw)
    return lid, round(len(x) / sr, 3), words


def align(text, heard, t_end):
    words = text.split()
    a, b = [norm(w) for w in words], [norm(h[2]) for h in heard]
    t0s, t1s = [None] * len(words), [None] * len(words)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            t0s[blk.a + k], t1s[blk.a + k] = heard[blk.b + k][0], heard[blk.b + k][1]
    known = [i for i, v in enumerate(t0s) if v is not None]
    for i in range(len(words)):
        if t0s[i] is None:
            prev = max([k for k in known if k < i], default=None)
            nxt = min([k for k in known if k > i], default=None)
            lo = t1s[prev] if prev is not None else 0
            hi = t0s[nxt] if nxt is not None else t_end
            n_lo, n_hi = (prev if prev is not None else -1), (nxt if nxt is not None else len(words))
            span = (hi - lo) / max(1, n_hi - n_lo - 1)
            t0s[i] = lo + span * (i - n_lo - 1)
            t1s[i] = t0s[i] + span
    return [[w, round(a0, 3), round(min(t_end, max(a0 + 0.05, a1)), 3)] for w, a0, a1 in zip(words, t0s, t1s)]


def chunks(words, max_words):
    out, sentence = [], []
    for w in words:
        sentence.append(w)
        if re.search(r"[.?!]$", w[0]):
            n = math.ceil(len(sentence) / max_words)
            size = math.ceil(len(sentence) / n)
            out += [sentence[i:i + size] for i in range(0, len(sentence), size)]
            sentence = []
    if sentence:
        n = math.ceil(len(sentence) / max_words)
        size = math.ceil(len(sentence) / n)
        out += [sentence[i:i + size] for i in range(0, len(sentence), size)]
    return out


# ---------- plan ----------
def build(slug, video, fmt):
    wide = fmt == "wide"
    key = "vo" if wide else "short"
    vo_dir = os.path.join(ROOT, slug, "vo")
    scenes = [s for s in video["scenes"] if s.get(key)]
    plan = {"format": fmt, "size": [1920, 1080] if wide else [1080, 1920], "fps": 30, "voice": VOICE, "slug": slug,
            "segments": [], "vo": [], "bites": [], "captions": [], "cues": [], "sections": []}
    cue = lambda t, k, **o: plan["cues"].append({"t": round(t, 3), "k": k, **o})
    chapters = []

    def say(text, at):
        lid, dur, heard = speak(vo_dir, text)
        words = align(text, heard, dur)
        plan["vo"].append({"id": lid, "t": round(at, 3), "dur": dur})
        ch = chunks(words, 7 if wide else 4)
        for i, c in enumerate(ch):
            end = at + (ch[i + 1][0][1] if i + 1 < len(ch) else dur + 0.15)
            plan["captions"].append({"t0": round(at + c[0][1] - 0.04, 3), "t1": round(end, 3), "who": "vo",
                                     "words": [[w, round(at + a, 3), round(at + b, 3)] for w, a, b in c]})
        used = [-1]

        def when(anchor, fallback):
            """Time of the first spoken word matching anchor, after the previous anchor."""
            if not anchor:
                return fallback
            a = norm(anchor)
            for i, w in enumerate(words):
                if i > used[0] and (norm(w[0]) == a or (len(a) > 3 and norm(w[0]).startswith(a))):
                    used[0] = i
                    return at + w[1]
            return fallback
        return at + dur, when

    n_scenes = sum(1 for s in scenes if s["kind"] == "scene")
    k = 0
    t = 0.0
    for s in scenes:
        if s["kind"] == "hook":
            end, _ = say(s[key], 0.35)
            t1 = snap(end + 0.45)
            plan["segments"].append({"kind": "hook", "t0": 0, "t1": t1, "lines": s["lines"], "mark": s["mark"], "kicker": s["kicker"]})
            plan["sections"].append({"t0": 0, "t1": t1, "kind": "hook"})
            chapters.append((0, "Intro"))
            cue(0.0, "swell"); cue(0.12, "slam"); cue(t1 - 1.2, "riser", d=1.2)
            t = t1
        elif s["kind"] == "scene":
            k += 1
            end, when = say(s[key], t + 0.45)
            t1 = snap(max(end + 0.6, t + 3.5))
            bullets = []
            for i, (icon, text, anchor) in enumerate(s.get("bullets", [])):
                bt = when(anchor, None)
                if bt is None:
                    if not wide:
                        continue  # the Short's shorter voiceover doesn't mention it: leave it out
                    bt = t + 0.7 + 0.35 * i
                bullets.append({"icon": icon, "text": text, "t": round(bt - 0.12, 3)})
                cue(bt - 0.12, "tick", v=0.75)
            vis = dict(s.get("visual") or {"type": "icon", "icon": "check"})
            if "at" in vis:
                vis["t"] = round(when(vis["at"], t + 1.0), 3)
            if vis["type"] == "maps" and vis.get("alarm"):
                vis["t_alarm"] = round(when(vis["alarm"], t + 1.5), 3)
            if vis["type"] == "maps" and vis["you_to"] != vis["you_from"]:
                vt = min(vis.get("t", t + 0.8), t + 0.8)  # start the climb early so it finishes on screen
                vis["t"] = round(vt, 3)
                t1 = max(t1, snap(vt + 2.8))
                cue(vt + 1.4, "success")
                for r in range(4):
                    cue(vt + 0.15 + r * 0.3, "pop", f=600 + 90 * r)
            elif vis["type"] in ("chat",):
                for r in range(3):
                    cue(vis["t"] + 0.1 + r * 0.35, "pop", f=560 + 80 * r)
                if vis.get("you") is not None:
                    cue(vis["t"] + 1.3, "success")
            elif vis["type"] == "ba":
                vis["wipe"] = [round(t + 1.0, 3), round(t + 1.9, 3)]
                cue(t + 1.0, "whoosh", d=0.9, up=0, v=0.8); cue(t + 1.85, "shimmer", d=0.7)
            elif vis["type"] in ("profile", "review"):
                cue(vis["t"], "pop", f=700)
            if vis.get("t_alarm"):
                cue(vis["t_alarm"], "thud")
            seg = {"kind": "scene", "t0": t, "t1": t1, "k": k, "of": n_scenes, "n": s.get("n"), "eyebrow": s["eyebrow"],
                   "title": s["title"], "bullets": bullets, "visual": vis}
            plan["segments"].append(seg)
            plan["sections"].append({"t0": t, "t1": t1, "kind": "groove"})
            if s.get("chapter"):
                chapters.append((t, s["chapter"]))
            cue(t - 0.28, "whoosh", d=0.5, up=1, v=0.7); cue(t + 0.06, "slam")
            if s.get("n"):
                cue(t + 0.1, "num", n=min(5, s["n"]))
            t = t1
        else:  # outro
            cue(t - 0.28, "whoosh", d=0.5, up=1, v=0.7)
            end, when = say(s[key], t + 0.7)
            url_t = when("window", end - 2.0) - 0.1
            t1 = snap(end + 1.7)
            plan["segments"].append({"kind": "outro", "t0": t, "t1": t1, "url": round(url_t, 3), "hit": round(t1 - 1.5, 3), "head": s["head"]})
            plan["sections"].append({"t0": t, "t1": t1, "kind": "outro"})
            chapters.append((t, "Free audit"))
            for i in range(4):
                cue(t + 0.1 + i * 0.07, "whoosh", d=0.4, up=1, v=0.35)
            cue(t + 0.75, "lock"); cue(t + 1.75, "swipe"); cue(t + 2.3, "pop", f=440)
            for i in range(len("windowfilmmarketingagency.com")):
                cue(url_t + i * 0.034, "key", v=0.6)
            cue(t1 - 1.5, "final")
            t = t1
    plan["duration"] = t
    plan["cues"].sort(key=lambda c: c["t"])
    # YouTube chapters: start at 0:00, at least 10 s each. A short chapter folds into the one before it
    # (a short intro hands 0:00 to the next chapter).
    merged = list(chapters)
    while len(merged) > 1:
        short = [i for i in range(len(merged)) if (merged[i + 1][0] if i + 1 < len(merged) else t) - merged[i][0] < 10]
        if not short:
            break
        i = short[0]
        if i == 0:
            merged[1] = (0, merged[1][1])
        merged.pop(i)
    return plan, [(f"{int(ct // 60)}:{int(ct % 60):02d}", name) for ct, name in merged]


if __name__ == "__main__":
    for slug, video in VIDEOS.items():
        if ONLY and slug not in ONLY:
            continue
        print(slug)
        os.makedirs(os.path.join(ROOT, slug), exist_ok=True)
        for fmt in ("wide", "reel"):
            plan, chapters = build(slug, video, fmt)
            json.dump(plan, open(os.path.join(ROOT, slug, f"plan-{fmt}.json"), "w"), indent=1)
            if fmt == "wide":
                json.dump(chapters, open(os.path.join(ROOT, slug, "chapters.json"), "w"))
            print(f"  {fmt}: {plan['duration']:.1f} s, {len(plan['segments'])} segments, {len(plan['captions'])} captions")
