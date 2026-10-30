#!/usr/bin/env python3
"""Music and sound design for the reel, synthesized from scratch (no samples).

    python3 video/audio.py cues.json out_dir/

Writes music.wav, sfx.wav and mix.wav (48 kHz stereo) to out_dir. cues.json comes from
`node video/render.mjs --cues cues.json`, so every sound effect lands on its frame.
The music is 120 BPM in A minor: it builds through the problem, cuts to silence at 21.86 s
and drops on "We get you found." at 22.0 s.
"""
import json
import os
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
DUR = 38.0
N = int(SR * (DUR + 0.6))
BEAT = 0.5
rng = np.random.default_rng(20261030)


# ---------- building blocks ----------
def tt(n):
    return np.arange(n) / SR


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, "bandpass" if kind == "band" else kind, fs=SR, output="sos"), x, axis=0)


def noise(n):
    return rng.standard_normal(n)


def pan2(x, p=0.0):
    a = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


def place(buf, sig, t, g=1.0, p=0.0):
    if sig.ndim == 1:
        sig = pan2(sig, p)
    i = int(round(t * SR))
    if i < 0:
        sig, i = sig[-i:], 0
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * g


def fade(x, fin=0.002, fout=0.01):
    a, b = int(fin * SR), int(fout * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def saw(f, n, ph=None):
    ph = rng.random() if ph is None else ph
    p = (ph + np.cumsum(np.broadcast_to(f, (n,))) / SR) % 1.0
    return 2 * p - 1


def sine(f, n, ph=0.0):
    return np.sin(2 * np.pi * (ph + np.cumsum(np.broadcast_to(f, (n,))) / SR))


def svf(x, fc, q=0.8, mode="bp"):
    """Chamberlin state-variable filter with a per-sample cutoff."""
    f = 2 * np.sin(np.pi * np.minimum(np.broadcast_to(fc, x.shape), SR / 7) / SR)
    qq = 1.0 / q
    low = band = 0.0
    y = np.empty_like(x)
    for i in range(len(x)):
        high = x[i] - low - qq * band
        band += f[i] * high
        low += f[i] * band
        y[i] = band if mode == "bp" else low if mode == "lp" else high
    return y


def make_ir(dur=2.2, decay=0.5, cutoff=6500):
    n = int(dur * SR)
    t = tt(n)
    ir = np.zeros((n + int(0.014 * SR), 2))
    for c in range(2):
        ir[int(0.014 * SR):, c] = filt(noise(n) * np.exp(-t / decay), "low", cutoff)
    return ir / np.sqrt(np.sum(ir ** 2) / 2)


def reverb(x, ir):
    return np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], axis=1)


def pingpong(x, d, fb=0.38, taps=6):
    y = np.zeros_like(x)
    mono = x.mean(axis=1)
    D = int(d * SR)
    for k in range(1, taps + 1):
        if k * D >= len(x):
            break
        y[k * D:, k % 2] += mono[: len(x) - k * D] * fb ** k
    return y


# ---------- drums and instruments ----------
def kick(v=1.0):
    n = int(0.5 * SR)
    t = tt(n)
    f = 47 + 115 * np.exp(-t / 0.045) + 60 * np.exp(-t / 0.007)
    body = sine(f, n) * np.exp(-t / 0.3)
    click = filt(noise(n), "high", 1800) * np.exp(-t / 0.004) * 0.3
    return fade(np.tanh(1.7 * (body + click)) * 0.85 * v, 0, 0.03)


def clap(v=1.0):
    n = int(0.45 * SR)
    t = tt(n)
    nz = filt(noise(n), "band", [900, 6500])
    x = np.zeros(n)
    for o in (0, 0.011, 0.023):
        i = int(o * SR)
        x[i:] += nz[i:] * np.exp(-t[: n - i] / 0.0075)
    x += nz * np.exp(-t / 0.14) * 0.55 * (t > 0.023)
    return fade(x * 0.75 * v, 0, 0.02)


def hat(open_=False, v=1.0):
    n = int((0.4 if open_ else 0.09) * SR)
    t = tt(n)
    x = filt(filt(noise(n), "high", 7200), "low", 15000)
    return fade(x * np.exp(-t / (0.11 if open_ else 0.02)) * 0.5 * v, 0, 0.005)


def snare(v=1.0):
    n = int(0.3 * SR)
    t = tt(n)
    body = sine(180 + 70 * np.exp(-t / 0.02), n) * np.exp(-t / 0.07)
    nz = filt(noise(n), "band", [1200, 9000]) * np.exp(-t / 0.1)
    return fade((body * 0.55 + nz * 0.8) * 0.7 * v, 0, 0.01)


def crash(v=1.0, decay=1.3):
    n = int(decay * 2.2 * SR)
    t = tt(n)
    x = filt(noise(n), "high", 3500) * np.exp(-t / decay) + filt(noise(n), "band", [5000, 11000]) * np.exp(-t / (decay * 0.6)) * 0.6
    return fade(x * 0.35 * v, 0.001, 0.05)


def bass(m, dur, v=1.0, cutoff=900):
    n = int(dur * SR)
    t = tt(n)
    f = mtof(m)
    x = 0.55 * saw(f, n) + 0.6 * sine(f, n) + 0.45 * sine(f / 2, n)
    x = filt(x, "low", cutoff)
    e = np.minimum(1, t / 0.005) * (0.72 + 0.28 * np.exp(-t / 0.09))
    return fade(x * e * 0.5 * v, 0.003, 0.03)


def pad_voice(midis, dur, cutoff, rel=0.7):
    n = int((dur + rel) * SR)
    t = tt(n)
    x = np.zeros(n)
    for m in midis:
        for d in (-0.09, 0.0, 0.08):
            x += saw(mtof(m) * 2 ** (d / 12), n)
    x = filt(x / (3 * len(midis)), "low", cutoff)
    e = np.clip(t / 0.3, 0, 1) * np.clip((dur + rel - t) / rel, 0, 1)
    return x * e


def pad(midis, dur, cutoff=1500, v=1.0):
    return np.stack([pad_voice(midis, dur, cutoff), pad_voice(midis, dur, cutoff)], axis=1) * v


def pluck(m, v=1.0, bright=3500, dur=0.4):
    n = int(dur * SR)
    t = tt(n)
    f = mtof(m)
    x = 0.6 * saw(f, n) + 0.4 * np.tanh(4 * sine(f, n))
    x = filt(x, "low", bright)
    return fade(x * np.exp(-t / 0.1) * np.minimum(1, t / 0.002) * 0.45 * v, 0, 0.02)


def bell(partials, dur, v=1.0, attack=0.002):
    n = int(dur * SR)
    t = tt(n)
    x = np.zeros(n)
    for f, a, d in partials:
        x += a * sine(f, n, rng.random()) * np.exp(-t / d)
    return fade(x * np.minimum(1, t / attack) * v, 0, 0.02)


# ---------- sound effects ----------
def sfx_whoosh(d=0.7, up=1, v=1.0):
    n = int(d * SR)
    u = np.linspace(0, 1, n)
    fc = 350 * 28 ** u if up else 7000 * (1 / 22) ** u
    shape = u ** 2 * (1 - u) ** 0.35 if up else (1 - u) ** 2 * u ** 0.35
    shape = shape / shape.max()
    x = svf(noise(n), fc, 1.4) * shape
    st = np.stack([x, np.roll(x, 90)], axis=1)
    return st * 0.55 * v


def sfx_key(v=1.0):
    n = int(0.03 * SR)
    t = tt(n)
    x = filt(noise(n), "band", [2200, 7500]) * np.exp(-t / 0.0022) * 0.9
    x += sine(150 + 40 * rng.random(), n) * np.exp(-t / 0.008) * 0.35
    return fade(x * 0.5 * v, 0, 0.004)


def sfx_enter():
    n = int(0.12 * SR)
    t = tt(n)
    return fade((filt(noise(n), "band", [700, 4000]) * np.exp(-t / 0.006) + sine(110, n) * np.exp(-t / 0.04) * 0.8) * 0.6, 0, 0.01)


def sfx_tick(v=1.0):
    n = int(0.04 * SR)
    t = tt(n)
    return fade((sine(2300, n) * np.exp(-t / 0.006) + filt(noise(n), "high", 4000) * np.exp(-t / 0.002) * 0.4) * 0.22 * v, 0, 0.004)


def sfx_swipe(v=1.0):
    n = int(0.28 * SR)
    u = np.linspace(0, 1, n)
    x = svf(noise(n), 1800 * 4 ** u, 1.6) * np.sin(np.pi * u) ** 2
    return x * 0.18 * v


def sfx_pop(f=520, v=1.0):
    n = int(0.12 * SR)
    t = tt(n)
    x = sine(f * (1 + 0.7 * np.minimum(1, t / 0.045)), n) * np.exp(-t / 0.05)
    x += filt(noise(n), "band", [1500, 6000]) * np.exp(-t / 0.002) * 0.25
    return fade(x * 0.35 * v, 0.001, 0.01)


def sfx_pin(f=800):
    n = int(0.2 * SR)
    t = tt(n)
    x = sine(f * (1.6 - 0.6 * np.minimum(1, t / 0.06)), n) * np.exp(-t / 0.07)
    x += sine(95, n) * np.exp(-t / 0.05) * 0.5
    return fade(x * 0.32, 0.001, 0.01)


def sfx_scroll(v=1.0):
    n = int(0.025 * SR)
    t = tt(n)
    return fade((filt(noise(n), "band", [1000, 5000]) * np.exp(-t / 0.003) + sine(900, n) * np.exp(-t / 0.004) * 0.4) * 0.28 * v, 0, 0.003)


def sfx_thud():
    n = int(0.35 * SR)
    t = tt(n)
    return fade((sine(72 - 20 * np.minimum(1, t / 0.1), n) * np.exp(-t / 0.15) + filt(noise(n), "low", 500) * np.exp(-t / 0.04) * 0.6) * 0.7, 0, 0.02)


def sfx_boom(v=1.0):
    n = int(2.2 * SR)
    t = tt(n)
    x = sine(36 + 70 * np.exp(-t / 0.12), n) * np.exp(-t / 0.9)
    x += filt(noise(n), "low", 1400) * np.exp(-t / 0.3) * 0.7
    x += filt(noise(n), "band", [150, 600]) * np.exp(-t / 0.08) * 0.6
    return fade(np.tanh(1.4 * x) * 0.85 * v, 0.001, 0.05)


def sfx_count(f=900):
    n = int(0.05 * SR)
    t = tt(n)
    return fade((sine(f, n) * np.exp(-t / 0.014) + sine(f * 2, n) * np.exp(-t / 0.008) * 0.3) * 0.18, 0.001, 0.005)


def sfx_chaching():
    out = np.zeros((int(1.8 * SR), 2))
    for o in (0.0, 0.065):
        n = int(0.12 * SR)
        place(out, filt(noise(n), "band", [2500, 9000]) * np.exp(-tt(n) / 0.025) * 0.45, o)
    ching = bell([(2093, 1, 0.9), (2637 * 1.002, 0.8, 0.7), (3136, 0.6, 0.6), (4186 * 1.003, 0.4, 0.4), (5274, 0.2, 0.25)], 1.7)
    ching *= 1 + 0.25 * np.sin(2 * np.pi * 17 * tt(len(ching)))
    place(out, ching * 0.22, 0.11, p=-0.1)
    place(out, ching * 0.18, 0.125, p=0.2)
    for k in range(9):
        n = int(0.08 * SR)
        f = 3000 + rng.random() * 3500
        place(out, sine(f, n) * np.exp(-tt(n) / 0.02) * 0.08, 0.15 + k * 0.045 + rng.random() * 0.02, p=rng.uniform(-0.8, 0.8))
    return out


def sfx_shimmer(d=0.8):
    n = int(d * SR)
    u = np.linspace(0, 1, n)
    out = np.zeros((n, 2))
    for k in range(14):
        f = 2600 + rng.random() * 6500
        x = sine(f, n, rng.random()) * (0.5 + 0.5 * np.sin(2 * np.pi * (8 + rng.random() * 10) * tt(n)))
        out += pan2(x, rng.uniform(-0.9, 0.9))
    return out * (np.sin(np.pi * u) ** 2)[:, None] * 0.018


def sfx_ring():
    """One burst of a two-tone phone trill, through a small-speaker band."""
    n = int(0.62 * SR)
    t = tt(n)
    sel = (np.floor(t * 22) % 2).astype(bool)
    f = np.where(sel, 1280.0, 1020.0)
    x = np.tanh(2.2 * sine(f, n)) * (t < 0.44) * np.minimum(1, t / 0.01)
    x = filt(x, "band", [500, 3800])
    return fade(x * 0.2, 0.002, 0.05)


def sfx_heart(v=1.0):
    n = int(0.45 * SR)
    t = tt(n)
    x = sine(58, n) * np.exp(-t / 0.09) * np.minimum(1, t / 0.004)
    y = np.zeros(n)
    i = int(0.15 * SR)
    y[i:] = x[: n - i] * 0.65
    return fade(np.tanh(2 * (x + y)) * 0.75 * v, 0, 0.02)


def sfx_riser(d=1.86):
    n = int(d * SR)
    u = np.linspace(0, 1, n)
    x = svf(noise(n), 250 * 40 ** u, 2.2) * u ** 2.2
    tone = filt(saw(180 * 7 ** u, n), "low", 2500) * u ** 3 * 0.3
    s = np.stack([x + tone, np.roll(x, 120) + tone], axis=1) * 0.5
    s[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))[:, None]
    return s


def sfx_drop():
    out = np.zeros((int(3 * SR), 2))
    place(out, sfx_boom(1.15), 0)
    place(out, crash(1.0, 1.4), 0)
    n = int(0.25 * SR)
    place(out, filt(noise(n), "band", [300, 3000]) * np.exp(-tt(n) / 0.05) * 0.6, 0)
    return out


def sfx_slam(p=0.0):
    out = np.zeros((int(0.8 * SR), 2))
    n = int(0.5 * SR)
    t = tt(n)
    x = sine(85 - 30 * np.minimum(1, t / 0.08), n) * np.exp(-t / 0.13) + filt(noise(n), "low", 2600) * np.exp(-t / 0.05) * 0.8
    place(out, fade(np.tanh(1.5 * x) * 0.6, 0, 0.02), 0, p=p)
    place(out, sfx_whoosh(0.22, 0, 0.5), 0, p=p)
    return out


def sfx_check():
    out = np.zeros((int(0.6 * SR), 2))
    place(out, bell([(1318.5, 1, 0.12), (2637, 0.3, 0.06)], 0.4) * 0.13, 0)
    place(out, bell([(1760, 1, 0.16), (3520, 0.3, 0.08)], 0.45) * 0.13, 0.06)
    return out


def sfx_stamp():
    n = int(0.4 * SR)
    t = tt(n)
    x = sine(120 - 40 * np.minimum(1, t / 0.06), n) * np.exp(-t / 0.1) + filt(noise(n), "band", [200, 2500]) * np.exp(-t / 0.035)
    return fade(np.tanh(1.3 * x) * 0.55, 0, 0.02)


def sfx_rank(f=700):
    n = int(0.07 * SR)
    t = tt(n)
    return fade((sine(f, n) * np.exp(-t / 0.02) + sine(f * 1.5, n) * np.exp(-t / 0.012) * 0.3) * 0.2, 0.001, 0.005)


def sfx_success():
    out = np.zeros((int(2 * SR), 2))
    for k, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
        place(out, bell([(f, 1, 0.5), (f * 2, 0.25, 0.25), (f * 3.01, 0.08, 0.12)], 1.2) * 0.14, k * 0.065, p=-0.3 + k * 0.2)
    return out


def sfx_ding():
    return bell([(1318.5, 1, 0.7), (1975.5, 0.55, 0.5), (2637, 0.25, 0.3)], 1.4) * 0.17


def sfx_lock():
    n = int(0.3 * SR)
    t = tt(n)
    x = filt(noise(n), "band", [3000, 9000]) * np.exp(-t / 0.004) + sine(1500, n) * np.exp(-t / 0.025) * 0.4 + sine(90, n) * np.exp(-t / 0.08) * 0.8
    return fade(x * 0.4, 0, 0.02)


def sfx_swell():
    n = int(1.2 * SR)
    u = np.linspace(0, 1, n)
    x = svf(noise(n), 250 * 8 ** u, 1.2) * np.sin(np.pi * u) ** 2 * 0.5 + sine(110, n) * np.sin(np.pi * u) ** 2 * 0.2
    return x


def sfx_final():
    out = np.zeros((int(3 * SR), 2))
    place(out, sfx_boom(0.7), 0)
    place(out, crash(0.7, 1.6), 0)
    for k, f in enumerate((1046.5, 1318.5, 1568.0)):
        place(out, bell([(f, 1, 1.0), (f * 2, 0.2, 0.4)], 2.5) * 0.11, 0.01 * k, p=(k - 1) * 0.4)
    return out


def build_sfx(cues):
    out = np.zeros((N, 2))
    for c in cues:
        k, t, v = c["k"], c["t"], c.get("v", 1.0)
        p = c.get("pan", 0.0)
        if k == "key":
            place(out, sfx_key(v), t, g=1.7, p=rng.uniform(-0.15, 0.15))
        elif k == "enter":
            place(out, sfx_enter(), t)
        elif k == "tick":
            place(out, sfx_tick(v), t)
        elif k == "swipe":
            place(out, sfx_swipe(), t)
        elif k == "pop":
            place(out, sfx_pop(c.get("f", 520), v), t, p=p)
        elif k == "whoosh":
            place(out, sfx_whoosh(c.get("d", 0.7), c.get("up", 1), v), t)
        elif k == "pin":
            place(out, sfx_pin(c.get("f", 800)), t)
        elif k == "scroll":
            place(out, sfx_scroll(v), t)
        elif k == "thud":
            place(out, sfx_thud(), t)
        elif k == "boom":
            place(out, sfx_boom(), t)
        elif k == "count":
            place(out, sfx_count(c.get("f", 900)), t)
        elif k == "chaching":
            place(out, sfx_chaching(), t)
        elif k == "shimmer":
            place(out, sfx_shimmer(c.get("d", 0.8)), t)
        elif k == "ring":
            place(out, sfx_ring(), t)
        elif k == "heart":
            place(out, sfx_heart(v), t)
        elif k == "riser":
            place(out, sfx_riser(c.get("d", 1.86)), t)
        elif k == "drop":
            place(out, sfx_drop(), t)
        elif k == "slam":
            place(out, sfx_slam(p), t)
        elif k == "check":
            place(out, sfx_check(), t)
        elif k == "stamp":
            place(out, sfx_stamp(), t)
        elif k == "rank":
            place(out, sfx_rank(c.get("f", 700)), t)
        elif k == "success":
            place(out, sfx_success(), t)
        elif k == "ding":
            place(out, sfx_ding(), t)
        elif k == "lock":
            place(out, sfx_lock(), t)
        elif k == "swell":
            place(out, sfx_swell(), t)
        elif k == "final":
            place(out, sfx_final(), t)
    return out


# ---------- music ----------
CHORDS = {"Am": [57, 60, 64, 69], "F": [57, 60, 65, 69], "C": [55, 60, 64, 67], "G": [55, 59, 62, 67], "E": [56, 59, 64, 68]}
ROOT = {"Am": 45, "F": 41, "C": 48, "G": 43, "E": 40}
PROG = [(0, 4, "Am"), (4, 6, "Am"), (6, 8, "F"), (8, 10, "Am"), (10, 12, "F"), (12, 14, "G"), (14, 16, "F"), (16, 18, "G"),
        (18, 19, "Am"), (19, 21.86, "E"), (22, 24, "F"), (24, 26, "G"), (26, 28, "Am"), (28, 30, "C"), (30, 32, "F"),
        (32, 34, "G"), (34, 36, "Am"), (36, 38.4, "C")]


def chord_at(t):
    for a, b, c in PROG:
        if a <= t < b:
            return c
    return None


def build_music():
    drums = np.zeros((N, 2))
    bassb = np.zeros((N, 2))
    pads = np.zeros((N, 2))
    arps = np.zeros((N, 2))
    kicks = []

    # pads, one voice per chord region
    for a, b, c in PROG:
        cut = 1150 if a < 8 else 1300 if a < 12 else 650 if a < 14 else 900 + (a - 14) * 350 if a < 19 else 1100 if a < 22 else 2600 if a < 34 else 1400
        v = 0.95 if a < 22 else 1.0
        if a == 12:  # G then the "buried" sink: filter closes after 12.75
            place(pads, pad(CHORDS[c], 0.75, 1300) * 0.8, a)
            place(pads, pad(CHORDS[c], 1.25, 450) * 0.7, a + 0.75)
            continue
        place(pads, pad(CHORDS[c], b - a, cut, v), a)

    def section(t):
        if t < 4: return "intro"
        if t < 8: return "verse"
        if t < 12.75: return "groove"
        if t < 14: return "sink"
        if t < 17.5: return "build"
        if t < 19: return "lift"
        if t < 21.86: return "tension"
        if t < 22: return "gap"
        if t < 30: return "drop"
        if t < 34: return "cta"
        if t < 36: return "break"
        return "end"

    # step through 16th notes
    for step in range(int(38 / 0.125)):
        t = step * 0.125
        s = section(t)
        pos = step % 16  # position in bar
        on_beat = pos % 4 == 0
        c = chord_at(t)
        hum = rng.uniform(0.85, 1.0)
        # kick
        if (s in ("groove", "lift", "drop", "cta") and on_beat) or (s == "verse" and pos in (0, 8)):
            v = 1.0 if s in ("drop", "cta") else 0.8 if s in ("groove", "lift") else 0.6
            place(drums, kick(v), t)
            if s in ("drop", "cta"):
                kicks.append(t)
        # clap on 2 and 4
        if s in ("groove", "lift", "drop", "cta") and pos in (4, 12):
            place(drums, clap(0.9 if s in ("drop", "cta") else 0.7), t, g=0.5)
        # hats
        if s == "intro" and t >= 0.25 and pos % 2 == 0:
            place(drums, hat(False, (0.5 if pos % 4 == 2 else 0.3) * hum), t, g=0.5, p=0.25)
        if s in ("verse", "groove", "build", "lift", "drop", "cta"):
            if s in ("drop", "cta") and pos % 4 == 2:
                place(drums, hat(True, 0.9 * hum), t, g=0.35, p=0.2)
            elif s in ("build", "drop", "cta") or pos % 2 == 0:
                place(drums, hat(False, (0.55 if pos % 2 == 0 else 0.35) * hum), t, g=0.45, p=0.25)
        # bass
        if c and s in ("groove", "lift", "drop", "cta") and pos % 2 == 0:
            m = ROOT[c] + (12 if s in ("drop", "cta") and pos in (6, 14) else 0)
            place(bassb, bass(m, 0.22, 0.95 if s in ("drop", "cta") else 0.8, 1100 if s in ("drop", "cta") else 800), t)
        if c and s == "break" and on_beat:
            place(bassb, bass(ROOT[c], 0.45, 0.6, 600), t)
        if c and s == "build" and on_beat:
            place(bassb, bass(ROOT[c], 0.4, 0.6, 600), t)
        if c and s == "tension" and pos % 2 == 0:
            place(bassb, bass(ROOT[c], 0.2, 0.55 + 0.25 * (t - 19) / 3, 500 + 300 * (t - 19)), t)
        # arpeggio (16ths)
        if c and s in ("verse", "groove", "build", "lift", "drop", "cta") or (c and s in ("intro", "break") and pos % 2 == 0 and t >= 0.5):
            notes = [m + 12 for m in CHORDS[c]]
            idx = [0, 1, 2, 3, 2, 1, 3, 2][pos % 8]
            oct_ = 12 if (s == "build" and t >= 16) or s == "lift" else 0
            bright = {"intro": 1300, "verse": 1800, "groove": 2600, "build": 1800 + (t - 14) * 700, "lift": 4200, "drop": 4800, "cta": 4200, "break": 2400}[s]
            v = {"intro": 0.45, "verse": 0.6, "groove": 0.7, "build": 0.6 + (t - 14) * 0.08, "lift": 0.9, "drop": 1.0, "cta": 0.85, "break": 0.85}[s]
            place(arps, pluck(notes[idx] + oct_, v * hum, bright), t)
    # snare roll into the drop
    t = 21.0
    while t < 21.86:
        step = 0.25 if t < 21.5 else 0.125 if t < 21.75 else 0.0625
        place(drums, snare(0.35 + 0.65 * (t - 21) / 0.86), t, g=0.55)
        t += step
    # lift out of the break into the final hit
    place(drums, sfx_riser(1.0) * 0.6, 35.0)
    # accents
    place(drums, crash(0.8), 17.5)
    place(drums, kick(0.9), 17.5)
    place(drums, crash(1.0, 1.6), 22.0)
    place(drums, crash(0.6), 30.0)
    place(drums, kick(1.0), 36.0)
    place(drums, crash(0.9, 1.8), 36.0)
    for k, m in enumerate(CHORDS["C"] + [72]):
        place(arps, pluck(m + 12, 0.9, 5000, 1.2), 36.0 + k * 0.03)

    # sidechain duck for the groove sections
    duck = np.ones(N)
    tn = tt(N)
    for k in kicks:
        i = int(k * SR)
        j = min(N, i + int(0.35 * SR))
        duck[i:j] = np.minimum(duck[i:j], 1 - 0.55 * np.exp(-(tn[i:j] - k) / 0.11))
    bassb *= duck[:, None]
    pads *= duck[:, None]
    arps_d = arps * duck[:, None]

    ir = make_ir()
    arp_bus = arps_d + pingpong(arps_d, 0.375, 0.35) * 0.55
    music = drums * 0.9 + bassb * 0.6 + pads * 0.34 + arp_bus * 0.22
    music += reverb(pads * 0.34 + arp_bus * 0.22 + drums * 0.06, ir) * 0.28
    # hard cut before the drop, and a fade at the very end
    g = np.ones(N)
    g[(tn >= 21.86) & (tn < 22.0)] = 0
    g *= np.clip((38.0 - tn) / 1.4, 0, 1)
    # section levels: lift the quiet hook and the build so they hold up on phone speakers
    g *= np.interp(tn, [0, 3.9, 4.2, 13.9, 14.2, 17.3, 17.5, 33.9, 34.1], [2.1, 2.1, 1.2, 1.2, 1.6, 1.6, 1.0, 1.0, 1.5])
    return music * g[:, None]


def norm(x, peak=0.89):
    return x * (peak / max(1e-9, np.max(np.abs(x))))


def save(path, x):
    wavfile.write(path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))


if __name__ == "__main__":
    cues = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    sfx = build_sfx(cues)
    sfx += reverb(sfx, make_ir(1.4, 0.3)) * 0.12
    music = build_music()
    music, sfx = norm(music, 0.8), norm(sfx, 0.8)
    mix = norm(np.tanh(1.2 * (music * 0.72 + sfx * 0.8)))
    save(os.path.join(out, "music.wav"), norm(music))
    save(os.path.join(out, "sfx.wav"), norm(sfx))
    save(os.path.join(out, "mix.wav"), mix)
    rms = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
    print("rms dBFS: music %.1f  sfx %.1f  mix %.1f" % (rms(music), rms(sfx), rms(mix)))
