#!/usr/bin/env python3
"""Sound mix for "5 Videos Every Window Film Company Should Post".

    python3 video/five_audio.py <assets-dir> reel|wide

Reads plan-<format>.json (from five_build.py) and writes <assets-dir>/audio/<format>-mix.wav
(48 kHz stereo): the Gemini voiceover, the real audio of the footage where the plan uses it,
a 120 BPM music bed that ducks under speech, and sound effects on the plan's cues.
Instruments and effects come from audio.py.
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, resample_poly

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio as A  # noqa: E402

ASSETS, FMT = os.path.abspath(sys.argv[1]), sys.argv[2]
plan = json.load(open(os.path.join(ASSETS, f"plan-{FMT}.json")))
SR = A.SR
DUR = plan["duration"]
N = int(SR * (DUR + 0.3))
tn = np.arange(N) / SR


def level(x, target_db=-17.0):
    """Gain that puts the loud parts of a speech clip (90th percentile of 50 ms RMS) at target_db."""
    m = x.mean(axis=1) if x.ndim > 1 else x
    w = int(0.05 * SR)
    rms = np.sqrt(np.mean(m[: len(m) // w * w].reshape(-1, w) ** 2, axis=1) + 1e-12)
    return 10 ** (target_db / 20) / np.percentile(rms, 90)


# ---------- speech ----------
speech = np.zeros((N, 2))
for v in plan["vo"]:
    sr, x = wavfile.read(os.path.join(ASSETS, "vo", v["id"] + ".wav"))
    x = resample_poly(x.astype(np.float64) / 32768.0, SR, sr)
    A.place(speech, x * level(x) * np.sqrt(2), v["t"])  # centre-panned mono loses 3 dB per channel; match the stereo clips
bites = []
for b in plan["bites"]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(b["s0"]), "-t", str(b["s1"] - b["s0"]), "-i", os.path.join(ASSETS, "src", b["clip"] + ".mp4"),
                          "-vn", "-ac", "2", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64).reshape(-1, 2) / 32768.0
    x = A.filt(x, "high", 90)
    f = int(0.02 * SR)
    x[:f] *= np.linspace(0, 1, f)[:, None]
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    A.place(speech, x * b["gain"], b["t"])
    bites.append((b, len(x)))

# One gain per source clip (not per cut), so the quiet words in a clip stay quiet next to its loud ones.
for clip in {b["clip"] for b, _ in bites}:
    parts = [(int(b["t"] * SR), n) for b, n in bites if b["clip"] == clip]
    g = level(np.concatenate([speech[i:i + n] for i, n in parts]))
    for i, n in parts:
        speech[i:i + n] *= g

# ---------- music ----------
kind_at = lambda t: next((s["kind"] for s in plan["sections"] if s["t0"] <= t < s["t1"]), "outro")
outro = next(s for s in plan["segments"] if s["kind"] == "outro")
HIT = outro["hit"]
PROG = ["Am", "F", "C", "G"]
drums, bassb, pads, arps = (np.zeros((N, 2)) for _ in range(4))
kicks = []
for bar in range(int(DUR // 4) + 1):  # one chord every two bars
    t = bar * 4.0
    if t >= HIT:
        break
    c = PROG[bar % 4]
    k = kind_at(t)
    A.place(pads, A.pad(A.CHORDS[c], min(4.0, HIT - t), {"hook": 1000, "groove": 1500, "thin": 800, "outro": 2200}[k], 1.0), t)
for st in range(int(HIT / 0.125)):
    t = st * 0.125
    k, pos, c = kind_at(t), st % 16, PROG[int(t // 4) % 4]
    hum = A.rng.uniform(0.85, 1.0)
    if k in ("groove", "outro"):
        if pos % 4 == 0:
            A.place(drums, A.kick(0.9), t)
            kicks.append(t)
        if pos in (4, 12):
            A.place(drums, A.clap(0.8), t, g=0.5)
        if pos % 2 == 0:
            A.place(drums, A.hat(pos % 4 == 2 and k == "outro", 0.55 * hum), t, g=0.42, p=0.25)
        else:
            A.place(drums, A.hat(False, 0.28 * hum), t, g=0.4, p=-0.2)
        if pos % 2 == 0:
            A.place(bassb, A.bass(A.ROOT[c] + (12 if pos in (6, 14) else 0), 0.22, 0.9, 950), t)
        notes = [m + 12 for m in A.CHORDS[c]]
        A.place(arps, A.pluck(notes[[0, 1, 2, 3, 2, 1, 3, 2][pos % 8]], (0.9 if k == "outro" else 0.75) * hum, 4200 if k == "outro" else 3000), t)
    elif k == "hook":
        if t >= 0.5 and pos % 2 == 0:
            A.place(drums, A.hat(False, (0.5 if pos % 4 == 2 else 0.3) * hum), t, g=0.45, p=0.25)
            A.place(arps, A.pluck([m + 12 for m in A.CHORDS[c]][[0, 2, 1, 3][(pos // 2) % 4]], 0.55 * hum, 1800), t)
    else:  # thin: the footage's own audio is playing
        if pos % 4 == 0:
            A.place(drums, A.hat(False, 0.35 * hum), t, g=0.4, p=0.25)
        if pos == 0:
            A.place(bassb, A.bass(A.ROOT[c], 1.6, 0.5, 500), t)
first_item = plan["segments"][1]["t0"]
A.place(drums, A.crash(0.8, 1.3), first_item)
A.place(drums, A.kick(1.0), HIT)
A.place(drums, A.crash(0.9, 1.8), HIT)
for i, m in enumerate(A.CHORDS["C"] + [72]):
    A.place(arps, A.pluck(m + 12, 0.9, 5000, 1.4), HIT + i * 0.03)
A.place(pads, A.pad(A.CHORDS["C"], DUR - HIT, 2400, 1.0), HIT)

side = np.ones(N)
for kt in kicks:
    i, j = int(kt * SR), min(N, int(kt * SR) + int(0.35 * SR))
    side[i:j] = np.minimum(side[i:j], 1 - 0.5 * np.exp(-(tn[i:j] - kt) / 0.11))
bus = arps * side[:, None]
bus = bus + A.pingpong(bus, 0.375, 0.35) * 0.5
music = drums * 0.9 + bassb * side[:, None] * 0.6 + pads * side[:, None] * 0.36 + bus * 0.22
music += A.reverb(pads * 0.36 + bus * 0.22 + drums * 0.06, A.make_ir()) * 0.26
music /= np.max(np.abs(music)) + 1e-9

# duck the music under speech (fast down, slow back up), and further while clip audio plays
w = int(0.03 * SR)
env = np.sqrt(np.maximum(fftconvolve(speech.mean(axis=1) ** 2, np.ones(w) / w, mode="same"), 0))
talk = (env > 10 ** (-38 / 20)).astype(np.float64)
hold = int(0.35 * SR)
talk = fftconvolve(talk, np.ones(hold), mode="full")[:N].clip(0, 1)          # hold through short pauses
talk = fftconvolve(np.roll(talk, -int(0.10 * SR)), np.hanning(int(0.24 * SR)) / np.hanning(int(0.24 * SR)).sum(), mode="same")  # look ahead and smooth
thin = np.zeros(N)
for s in plan["sections"]:
    if s["kind"] == "thin":
        thin[int(s["t0"] * SR): int(s["t1"] * SR)] = 1
thin = fftconvolve(thin, np.hanning(int(0.3 * SR)) / np.hanning(int(0.3 * SR)).sum(), mode="same")
gain = (1 - 0.78 * talk) * (1 - 0.5 * thin) * np.clip((DUR - tn) / 1.3, 0, 1)
music *= gain[:, None]

# ---------- effects ----------
NOTE = [440.0, 523.25, 587.33, 659.25, 783.99]
sfx = np.zeros((N, 2))
for c in plan["cues"]:
    k, t, v, p = c["k"], c["t"], c.get("v", 1.0), c.get("pan", 0.0)
    if t < 0:
        continue
    if k == "whoosh":
        A.place(sfx, A.sfx_whoosh(c.get("d", 0.6), c.get("up", 1), v), t)
    elif k == "slam":
        A.place(sfx, A.sfx_slam(p), t, g=0.8)
    elif k == "num":
        f = NOTE[c["n"] - 1]
        A.place(sfx, A.bell([(f, 1, 0.55), (f * 2, 0.3, 0.3), (f * 3.01, 0.08, 0.15)], 1.3) * 0.2, t)
    elif k == "pop":
        A.place(sfx, A.sfx_pop(c.get("f", 520), v), t, p=p)
    elif k == "tick":
        A.place(sfx, A.sfx_tick(v), t)
    elif k == "swipe":
        A.place(sfx, A.sfx_swipe(), t)
    elif k == "ding":
        A.place(sfx, A.sfx_ding(), t)
    elif k == "shimmer":
        A.place(sfx, A.sfx_shimmer(c.get("d", 0.7)), t)
    elif k == "success":
        A.place(sfx, A.sfx_success(), t)
    elif k == "riser":
        A.place(sfx, A.sfx_riser(c.get("d", 1.2)), t, g=0.8)
    elif k == "swell":
        A.place(sfx, A.sfx_swell(), t)
    elif k == "lock":
        A.place(sfx, A.sfx_lock(), t)
    elif k == "key":
        A.place(sfx, A.sfx_key(v), t, g=1.5, p=A.rng.uniform(-0.15, 0.15))
    elif k == "final":
        A.place(sfx, A.sfx_final(), t)
sfx += A.reverb(sfx, A.make_ir(1.4, 0.3)) * 0.1
sfx /= np.max(np.abs(sfx)) + 1e-9

mix = np.tanh(1.1 * (speech * 1.0 + music * 0.5 + sfx * 0.42))
mix *= 0.89 / np.max(np.abs(mix))
out = os.path.join(ASSETS, "audio")
os.makedirs(out, exist_ok=True)
save = lambda name, x: wavfile.write(os.path.join(out, f"{FMT}-{name}.wav"), SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
save("mix", mix)
save("speech", speech * 0.89 / max(1e-9, np.max(np.abs(speech))))
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
sp = env > 10 ** (-38 / 20)
print(f"{FMT}: {DUR:.1f} s | speech {db(speech[sp]):.1f} dB | music under speech {db(music[sp] * 0.5):.1f} dB, in gaps {db(music[~sp] * 0.5):.1f} dB | sfx {db(sfx * 0.42):.1f} dB")
