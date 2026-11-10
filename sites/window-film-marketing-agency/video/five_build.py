#!/usr/bin/env python3
"""Voiceover and edit plan for "5 Videos Every Window Film Company Should Post".

    GEMINI_API_KEY=... python3 video/five_build.py <assets-dir> [--voice Orus]

<assets-dir> holds the footage cut into frames (frames/<clip>/00001.jpg at 30 fps, stills/) and
the source clips (src/owner.mp4, src/temp.mp4). This script
  1. speaks every script line with Gemini TTS into <assets-dir>/vo/ (cached by text + voice),
  2. transcribes each line locally (faster-whisper) to time the captions word by word,
  3. writes plan-reel.json (9:16, short) and plan-wide.json (16:9, longer): segments, footage
     cuts, on-screen text, captions, sound cues and music sections, all timed to the voice.
five-videos.html draws a plan; five_audio.py mixes voice, real clip audio, music and effects.
"""
import base64
import difflib
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

import numpy as np
from scipy.io import wavfile

ASSETS = os.path.abspath(sys.argv[1])
VOICE = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else "Orus"
MODEL = "gemini-3.8-flash-tts"
STYLE = "Confident, upbeat and direct, like a sharp marketing coach talking to contractors. Brisk, natural pace with clear diction."
VO_DIR = os.path.join(ASSETS, "vo")
os.makedirs(VO_DIR, exist_ok=True)

# ---------- script ----------
LINES = {
    # reel
    "r_hook": "Five videos every window film company should post.",
    "r_1": "One. The before and after. Same glass, completely different room.",
    "r_2": "Two. The install time-lapse. A full job in seconds.",
    "r_3": "Three. The client testimonial. Let your customers do the selling.",
    "r_4": "Four. The owner on camera, explaining why film matters.",
    "r_5": "Five. The temperature test.",
    "r_out": "Shoot them on your phone. We'll edit and post them for you. Window Film Marketing Agency dot com.",
    # longer video
    "w_intro": "If you install window film, your best marketing is already on your phone. Here are five videos every window film company should post, and how to shoot each one.",
    "w_1": "Number one. The before and after. Film is hard to see in a photo, so show the change. Stand in the same spot, shoot the glass before you start, and again when you're done. Put them side by side, and the result sells itself.",
    "w_2": "Number two. The install time-lapse. Prop your phone up, hit record, and let it run for the whole job. Sped up, people watch a full install in seconds, and they see how clean your crew works.",
    "w_3": "Number three. The client testimonial. Nothing sells like a happy customer saying it for you. Ask on install day, right in front of the finished glass. No video yet? Put your best Google reviews on screen.",
    "w_4a": "Number four. The owner on camera. Explain, in plain English, why the film matters. Here's a real installer doing exactly that.",
    "w_4b": "Short, specific, and it builds trust before they ever call.",
    "w_5a": "Number five. The temperature test. Grab an infrared thermometer and measure the same floor twice. Once behind the film, and once in direct sun.",
    "w_5b": "Thirty-eight degrees. Numbers like that turn a maybe into an estimate request.",
    "w_out": "That's five videos, all shot on a phone. Rather be installing than editing? Send us the clips. We'll edit them, caption them, and post them for you. Window Film Marketing Agency dot com.",
}

# Real audio from the footage: (clip, start, end, caption text)
BITES = {
    "owner_short": ("owner", 24.76, 29.95, "So I really want you guys to consider putting security film on your back sliding doors"),
    "owner_long": ("owner", 24.76, 41.9, "So I really want you guys to consider putting security film on your back sliding doors and anywhere else that you feel that access is easy. And this will give you at least a minute to a minute and a half if they decide to try to break through your glass instead of being able to enter in one second."),
    "temp_spot": ("temp", 11.56, 16.05, "And then we got this spot over here with the tinted glass. Check this out."),
    "temp_85": ("temp", 20.05, 22.7, "So, 85."),
    "temp_123": ("temp", 27.2, 32.65, "Call it 122, 123 over here in the sun. So that is the difference."),
}
BITE_GAIN = {"owner": 1.0, "temp": 5.0}  # the thermometer clip was recorded much quieter
# Word timings the transcriber got wrong (quiet, mumbled numbers), set from the clip's loudness curve:
# (clip, replace words starting in [from, to), with these)
WORD_FIXES = [("temp", 19.0, 22.6, [[20.2, 20.45, "So,"], [21.8, 22.4, "85."]]),
              ("temp", 26.0, 30.0, [[27.5, 27.68, "Call"], [27.68, 27.82, "it"], [27.9, 28.4, "122,"], [28.42, 28.9, "123"],
                                    [29.2, 29.34, "over"], [29.34, 29.52, "here"], [29.52, 29.6, "in"], [29.6, 29.68, "the"], [29.68, 29.84, "sun."]])]

ITEMS = [
    {"title": "Before & After", "kicker": "Privacy frost film · Pasadena, CA",
     "tips": [("Same spot, same angle", "stand"), ("Shoot it before, then after", "shoot"), ("Put them side by side", "put")]},
    {"title": "Install Time-Lapse", "kicker": "Frost film install · Pasadena, CA",
     "tips": [("Prop the phone up", "prop"), ("Record the whole job", "record"), ("Speed it up to seconds", "sped")]},
    {"title": "Client Testimonial", "kicker": "Real Google reviews",
     "tips": [("Ask on install day", "ask"), ("Film by the finished glass", "front"), ("No video yet? Show your reviews", "reviews")]},
    {"title": "The Owner Explains", "kicker": "Owner · MD Window Films",
     "tips": [("Plain English, no jargon", "plain"), ("One reason the film matters", "why"), ("Short and specific", "short")]},
    {"title": "Temperature Test", "kicker": "Infrared thermometer, same floor",
     "tips": [("Use an infrared thermometer", "infrared"), ("Behind the film vs. direct sun", "once"), ("Let the numbers sell", "numbers")]},
]

norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())


# ---------- voice ----------
def tts(text):
    body = {"model": MODEL,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text, "annotations": [{"type": "speech_metadata", "style": STYLE}]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": VOICE}]}}
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=json.dumps(body).encode(),
                                 headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
    for attempt in range(8):  # the TTS model is rate limited per minute: wait and retry on 429
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
    raise RuntimeError("no audio in response: " + json.dumps(j)[:300])


def speak_all():
    """Returns {id: {"dur": seconds, "words": [[t0, t1, word], ...]}} for every script line."""
    meta_path = os.path.join(VO_DIR, "lines.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    for lid, text in LINES.items():
        h = hashlib.sha1(f"{MODEL}|{VOICE}|{STYLE}|{text}".encode()).hexdigest()[:12]
        wav = os.path.join(VO_DIR, lid + ".wav")
        if meta.get(lid, {}).get("hash") == h and os.path.exists(wav):
            continue
        raw = os.path.join(VO_DIR, lid + ".raw.wav")
        open(raw, "wb").write(tts(text))
        sr, x = wavfile.read(raw)
        x = x.astype(np.float32) / 32768.0
        if x.ndim > 1:
            x = x.mean(axis=1)
        # trim silence, keep a little air, and bring every line to the same level
        loud = np.where(np.abs(x) > 0.02 * np.max(np.abs(x)))[0]
        x = x[max(0, loud[0] - int(0.03 * sr)): min(len(x), loud[-1] + int(0.12 * sr))]
        x *= 10 ** (-20 / 20) / (np.sqrt(np.mean(x ** 2)) + 1e-9)
        x = np.tanh(x * 1.2) / 1.2
        wavfile.write(wav, sr, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        meta[lid] = {"hash": h, "dur": round(len(x) / sr, 3)}
        json.dump(meta, open(meta_path, "w"), indent=1)  # save as we go so a failed run keeps what it has
        print("spoke", lid, meta[lid]["dur"], "s")
    todo = [lid for lid in LINES if "words" not in meta[lid]]
    if todo:
        from faster_whisper import WhisperModel
        model = WhisperModel("small.en", device="cpu", compute_type="int8")
        for lid in todo:
            sr, x = wavfile.read(os.path.join(VO_DIR, lid + ".wav"))
            x16 = np.interp(np.arange(0, len(x), sr / 16000), np.arange(len(x)), x.astype(np.float32) / 32768.0).astype(np.float32)
            segs, _ = model.transcribe(x16, word_timestamps=True, beam_size=5)
            meta[lid]["words"] = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words]
            heard = " ".join(w[2] for w in meta[lid]["words"])
            ratio = difflib.SequenceMatcher(None, [norm(w) for w in LINES[lid].split()], [norm(w[2]) for w in meta[lid]["words"]]).ratio()
            print(f"  check {lid}: match {ratio:.2f} | {heard}")
        json.dump(meta, open(meta_path, "w"), indent=1)
    return meta


def align(text, heard, t_start, t_end):
    """Per-word [t0, t1] for the words of `text`, from the transcript's word times."""
    words = text.split()
    a, b = [norm(w) for w in words], [norm(h[2]) for h in heard]
    t0s = [None] * len(words)
    t1s = [None] * len(words)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            t0s[blk.a + k], t1s[blk.a + k] = heard[blk.b + k][0], heard[blk.b + k][1]
    known = [i for i, v in enumerate(t0s) if v is not None]
    for i in range(len(words)):
        if t0s[i] is None:  # spread unmatched words (numbers, "dot com") between their neighbours
            prev = max([k for k in known if k < i], default=None)
            nxt = min([k for k in known if k > i], default=None)
            lo = t1s[prev] if prev is not None else t_start
            hi = t0s[nxt] if nxt is not None else t_end
            n_lo, n_hi = (prev if prev is not None else -1), (nxt if nxt is not None else len(words))
            span = (hi - lo) / (n_hi - n_lo - 1 + 1e-9) if n_hi - n_lo > 1 else 0
            t0s[i] = lo + span * (i - n_lo - 1)
            t1s[i] = t0s[i] + span
    return [[w, round(max(t_start, a0), 3), round(min(t_end, max(a0 + 0.05, a1)), 3)] for w, a0, a1 in zip(words, t0s, t1s)]


def chunks(words, max_words):
    """Caption phrases: one sentence at a time, split into even pieces of at most max_words."""
    out, sentence = [], []
    for w in words:
        sentence.append(w)
        if re.search(r"[.?!]$", w[0]):
            out += _even(sentence, max_words)
            sentence = []
    return out + (_even(sentence, max_words) if sentence else [])


def _even(sentence, max_words):
    n = math.ceil(len(sentence) / max_words)
    size = math.ceil(len(sentence) / n)
    return [sentence[i:i + size] for i in range(0, len(sentence), size)]


def clip_words(clip):
    path = os.path.join(ASSETS, "src", clip + ".words.json")
    if not os.path.exists(path):
        from faster_whisper import WhisperModel
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ASSETS, "src", clip + ".mp4"), "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
        audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
        segs, _ = WhisperModel("small.en", device="cpu", compute_type="int8").transcribe(audio, word_timestamps=True, vad_filter=True, beam_size=5)
        json.dump([[round(w.start, 2), round(w.end, 2), w.word.strip()] for s in segs for w in s.words], open(path, "w"))
    words = json.load(open(path))
    for c, a, b, fixed in WORD_FIXES:
        if c == clip:
            words = sorted([w for w in words if not a <= w[0] < b] + fixed)
    return words


# ---------- plan ----------
GRID = 0.5  # one beat at 120 BPM: segment starts land on the beat
snap = lambda t: math.ceil(t / GRID - 1e-6) * GRID


def build(fmt, vo_meta):
    wide = fmt == "wide"
    P = "w_" if wide else "r_"
    cap_words = 7 if wide else 4
    plan = {"format": fmt, "size": [1920, 1080] if wide else [1080, 1920], "fps": 30, "voice": VOICE,
            "segments": [], "vo": [], "bites": [], "captions": [], "cues": [], "sections": []}
    cue = lambda t, k, **o: plan["cues"].append({"t": round(t, 3), "k": k, **o})

    def say(lid, at):
        m = vo_meta[lid]
        words = align(LINES[lid], m["words"], 0, m["dur"])
        plan["vo"].append({"id": lid, "t": round(at, 3), "dur": m["dur"]})
        ch = chunks(words, cap_words)
        for i, c in enumerate(ch):
            end = at + (ch[i + 1][0][1] if i + 1 < len(ch) else m["dur"] + 0.15)
            plan["captions"].append({"t0": round(at + c[0][1] - 0.04, 3), "t1": round(end, 3), "who": "vo", "words": [[w, round(at + a, 3), round(at + b, 3)] for w, a, b in c]})
        when = lambda word, nth=0: at + [w for w in words if norm(w[0]) == word][nth][1]
        return at + m["dur"], when

    def bite(bid, at):
        clip, s0, s1, text = BITES[bid]
        heard = [h for h in clip_words(clip) if s0 - 0.3 <= h[0] <= s1 + 0.3]
        words = align(text, heard, s0 + 0.05, s1 - 0.05)
        plan["bites"].append({"id": bid, "clip": clip, "s0": s0, "s1": s1, "t": round(at, 3), "gain": BITE_GAIN[clip]})
        ch = chunks(words, cap_words)
        for i, c in enumerate(ch):
            end = at + ((ch[i + 1][0][1] if i + 1 < len(ch) else s1) - s0)
            plan["captions"].append({"t0": round(at + c[0][1] - s0 - 0.04, 3), "t1": round(end, 3), "who": "clip", "words": [[w, round(at + a - s0, 3), round(at + b - s0, 3)] for w, a, b in c]})
        when = lambda word, nth=0: at + [w for w in words if norm(w[0]) == word][nth][1] - s0
        return at + (s1 - s0), when, {"t0": round(at, 3), "t1": round(at + s1 - s0, 3), "src": clip, "s0": s0, "s1": s1, "zoom": 1.0}

    # hook
    end, when = say(P + ("intro" if wide else "hook"), 0.35)
    t1 = snap(end + 0.45)
    first = when("five")
    plan["segments"].append({"kind": "hook", "t0": 0, "t1": t1, "thumbs": [round((first if wide else 0.75) + 0.24 * i, 3) for i in range(5)]})
    plan["sections"].append({"t0": 0, "t1": t1, "kind": "hook"})
    cue(0.0, "swell"); cue(0.12, "slam")
    for i, tt in enumerate(plan["segments"][0]["thumbs"]):
        cue(tt, "pop", f=520 + 70 * i, pan=-0.6 + 0.3 * i)
    cue(t1 - 1.2, "riser", d=1.2)
    t = t1

    for n in range(1, 6):
        it = ITEMS[n - 1]
        seg = {"kind": "item", "n": n, "t0": t, "title": it["title"], "kicker": it["kicker"], "clips": [], "overlays": [], "tips": []}
        cue(t - 0.28, "whoosh", d=0.5, up=1, v=0.7); cue(t + 0.06, "slam", pan=0); cue(t + 0.1, "num", n=n)
        thin = []  # stretches where real clip audio plays and the music steps back
        lid = P + str(n) + ("a" if wide and n >= 4 else "")
        end, when = say(lid, t + 0.45)
        whens = [when]

        if n == 1:
            tw = when("change") - 0.1 if wide else when("after") - 0.15
            seg["media"] = {"type": "ba", "wipe": [round(tw, 3), round(tw + 0.9, 3)], "split": round(when("side") - 0.2, 3) if wide else None}
            cue(tw, "whoosh", d=0.9, up=0, v=0.8); cue(tw + 0.85, "shimmer", d=0.7)
            seg["overlays"] += [{"type": "chip", "text": "BEFORE", "pos": "tl", "style": "dark", "t0": t + 0.5, "t1": tw + 0.45},
                                {"type": "chip", "text": "AFTER", "pos": "tr", "style": "amber", "t0": tw + 0.55, "t1": 9e9}]
            if wide:
                seg["overlays"].append({"type": "chip", "text": "BEFORE", "pos": "tl", "style": "dark", "t0": when("side") + 0.3, "t1": 9e9})
            t1 = snap(max(end + 0.7, t + 6.0))
        elif n == 2:
            t1 = snap(end + 0.6)
            seg["clips"].append({"t0": t, "t1": t1, "src": "timelapse", "s0": 0.2, "s1": 30.6, "zoom": 1.0})
            seg["progress"] = True
            seg["overlays"].append({"type": "chip", "text": "TIME-LAPSE", "pos": "tl", "style": "amber", "icon": "ff", "t0": t + 0.5, "t1": 9e9})
            cue(t + 0.5, "pop", f=640)
        elif n == 3:
            t1 = snap(max(end + 0.6, t + 6.5))
            seg["clips"].append({"t0": t, "t1": t1, "src": "reviews", "s0": 1.15, "s1": 8.0, "zoom": 1.0})
            cue(t + 0.55, "ding")
        elif n == 4:
            tb = end + 0.3
            pre = tb - t
            s1 = 24.55
            seg["clips"].append({"t0": t, "t1": tb, "src": "owner", "s0": max(16.05, s1 - pre), "s1": s1, "zoom": 1.0})
            bend, bwhen, bclip = bite("owner_long" if wide else "owner_short", tb)
            bclip["zoom"] = 1.12
            seg["clips"].append(bclip)
            thin.append((tb - 0.2, bend + 0.1)); cue(tb, "tick", v=0.8)
            last = bend
            if wide:
                last, w2 = say("w_4b", bend + 0.35)
                whens.append(w2)
                seg["clips"].append({"t0": bend, "t1": 9e9, "src": "owner", "s0": 1.6, "s1": None, "zoom": 1.0})
            t1 = snap(last + (0.6 if wide else 0.35))
            seg["overlays"].append({"type": "lower", "text": "Owner", "sub": "MD Window Films", "t0": t + 0.6, "t1": 9e9})
        else:
            tb = end + 0.3
            if wide:
                seg["clips"].append({"t0": t, "t1": tb, "src": "temp", "s0": 2.4, "s1": 10.9, "zoom": 1.0})
                e0, _, c0 = bite("temp_spot", tb)
                seg["clips"].append(c0)
                tb = e0
            else:
                seg["clips"].append({"t0": t, "t1": tb, "src": "temp", "s0": 20.0 - (tb - t), "s1": 20.0, "zoom": 1.0})
            thin_start = seg["clips"][-1]["t0"] if wide else tb
            e1, w85, c1 = bite("temp_85", tb)
            e2, w123, c2 = bite("temp_123", e1)
            seg["clips"] += [c1, c2]
            thin.append((thin_start - 0.2, e2 + 0.1))
            tdiff, t123 = w123("that"), w123("123") - 0.1
            seg["overlays"] += [{"type": "big", "value": "85°F", "label": "behind the film", "color": "cool", "t0": w85("85") - 0.15, "t1": e1 - 0.2},
                                {"type": "big", "value": "123°F", "label": "in direct sun", "color": "hot", "t0": t123, "t1": tdiff},
                                {"type": "badge", "value": "38° cooler", "label": "behind the film", "t0": tdiff, "t1": 9e9}]
            cue(w85("85") - 0.15, "pop", f=420); cue(t123, "pop", f=760); cue(tdiff, "success")
            last = e2
            if wide:
                last, w2 = say("w_5b", e2 + 0.4)
                whens.append(w2)
                seg["clips"].append({"t0": e2, "t1": 9e9, "src": "temp", "s0": 24.6, "s1": 27.1, "zoom": 1.0})
            t1 = snap(last + (0.6 if wide else 0.3))

        seg["t1"] = t1
        for c in seg["clips"]:  # open-ended clips run to the end of the segment
            if c["t1"] > 1e8:
                c["t1"] = t1
                if c["s1"] is None:
                    c["s1"] = c["s0"] + (t1 - c["t0"])
        for o in seg["overlays"]:
            o["t0"], o["t1"] = round(o["t0"], 3), round(min(o["t1"], t1), 3)
        if wide:
            for text, anchor in it["tips"]:
                tt = next((w(anchor) for w in whens if _has(w, anchor)), None)
                seg["tips"].append({"text": text, "t": round(tt if tt is not None else t + 1.5, 3)})
                cue(seg["tips"][-1]["t"], "tick", v=0.7)
        # music: groove under the voice, pulled back while the clip's own audio plays
        cur = t
        for a, b in thin:
            if a > cur:
                plan["sections"].append({"t0": round(cur, 3), "t1": round(a, 3), "kind": "groove"})
            plan["sections"].append({"t0": round(a, 3), "t1": round(min(b, t1), 3), "kind": "thin"})
            cur = min(b, t1)
        if cur < t1:
            plan["sections"].append({"t0": round(cur, 3), "t1": t1, "kind": "groove"})
        plan["segments"].append(seg)
        t = t1

    # outro
    cue(t - 0.28, "whoosh", d=0.5, up=1, v=0.7)
    end, when = say(P + "out", t + 0.7)
    url_t = when("window") - 0.1
    t1 = snap(end + 1.7)
    plan["segments"].append({"kind": "outro", "t0": t, "t1": t1, "url": round(url_t, 3), "hit": round(t1 - 1.5, 3)})
    plan["sections"].append({"t0": t, "t1": t1, "kind": "outro"})
    for i in range(4):
        cue(t + 0.1 + i * 0.07, "whoosh", d=0.4, up=1, v=0.35)
    cue(t + 0.75, "lock"); cue(t + 1.75, "swipe"); cue(t + 2.3, "pop", f=440)
    for i in range(len("windowfilmmarketingagency.com")):
        cue(url_t + i * 0.034, "key", v=0.6)
    cue(t1 - 1.5, "final")
    plan["duration"] = t1
    plan["cues"].sort(key=lambda c: c["t"])
    return plan


def _has(when, word):
    try:
        when(word)
        return True
    except IndexError:
        return False


if __name__ == "__main__":
    meta = speak_all()
    for fmt in ("reel", "wide"):
        plan = build(fmt, meta)
        json.dump(plan, open(os.path.join(ASSETS, f"plan-{fmt}.json"), "w"), indent=1)
        print(f"plan-{fmt}.json: {plan['duration']:.1f} s, {len(plan['captions'])} captions, {len(plan['cues'])} cues")
        for s in plan["segments"]:
            print(f"   {s['t0']:6.1f}-{s['t1']:6.1f}  {s['kind']} {s.get('n', '')} {s.get('title', '')}")
