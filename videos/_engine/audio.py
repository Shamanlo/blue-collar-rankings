"""Mix voiceover + a synthesized music bed + scene whooshes into {project}/out/{format}-mix.wav.

    python3 _engine/audio.py <project> [landscape] [reel]

The music is generated here (no licensed tracks): soft keys, bass, light kick and shaker,
ducked under the voice.
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(sys.argv[1]).resolve()
OUT = HERE / "out"
SR = 48000
LEAD = 0.35  # matches tts.py
BPM = 96


def read_wav(path):
    with wave.open(str(path)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def tone(freq, dur, decay=2.5, harmonics=(1, .35, .12, .05)):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * decay) * np.minimum(1, t / 0.01)
    sig = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) for k, a in enumerate(harmonics))
    return sig * env


def add(buf, o, x):
    e = min(len(buf), o + len(x))
    if e > o:
        buf[o:e] += x[:e - o]


def music(total, rng):
    n = int(total * SR) + SR
    left = np.zeros(n)
    right = np.zeros(n)
    beat = 60 / BPM
    bar = beat * 4
    # D major: I - vi - IV - V  (D, Bm, G, A)
    chords = [[62, 66, 69, 74], [59, 62, 66, 71], [55, 59, 62, 67], [57, 61, 64, 69]]
    roots = [38, 35, 43, 45]
    t = 0.0
    i = 0
    while t < total:
        ch = chords[i % 4]
        s = int(t * SR)
        # keys: arpeggiated eighths, panned gently
        for k in range(8):
            note = ch[[0, 1, 2, 3, 2, 1, 2, 3][k]] + (12 if k == 4 else 0)
            x = tone(hz(note), beat * 1.5, decay=3.2) * 0.07
            o = s + int(k * beat / 2 * SR)
            pan = 0.5 + 0.3 * np.sin(k)
            add(left, o, x * (1 - pan) * 2)
            add(right, o, x * pan * 2)
        # pad
        pad = sum(tone(hz(m), bar, decay=0.6, harmonics=(1, .2)) for m in ch[:3]) * 0.025
        add(left, s, pad)
        add(right, s, pad)
        # bass on beats 1 and 3
        for b in (0, 2):
            x = tone(hz(roots[i % 4]), beat * 1.8, decay=2.2, harmonics=(1, .5, .2)) * 0.16
            o = s + int(b * beat * SR)
            add(left, o, x)
            add(right, o, x)
        # kick on 1 and 3, shaker on eighths
        for b in range(8):
            o = s + int(b * beat / 2 * SR)
            if b in (0, 4):
                kt = np.arange(int(0.25 * SR)) / SR
                kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * 0.22
                add(left, o, kick)
                add(right, o, kick)
            sh = rng.standard_normal(int(0.06 * SR))
            sh = np.diff(sh, prepend=0) * np.exp(-np.arange(len(sh)) / SR * 60) * (0.018 if b % 2 else 0.028)
            add(left, o, sh * 0.8)
            add(right, o, sh)
        t += bar
        i += 1
    return np.stack([left, right], 1)[: int(total * SR)]


def whoosh(rng, dur=0.45):
    x = rng.standard_normal(int(dur * SR))
    x = np.convolve(x, np.ones(24) / 24, mode="same")
    t = np.linspace(0, 1, len(x))
    return x * np.sin(np.pi * t) ** 2 * 0.06


def main(fmt):
    timings = json.loads((OUT / "timings.json").read_text())[fmt]
    total = timings[-1]["start"] + timings[-1]["dur"]
    rng = np.random.default_rng(7)
    vo = np.zeros(int(total * SR) + SR)
    fx = np.zeros_like(vo)
    for i, s in enumerate(timings):
        x = read_wav(HERE / s["audio"])
        o = int((s["start"] + LEAD) * SR)
        add(vo, o, x)
        if i:
            w = whoosh(rng)
            o = int(s["start"] * SR) - len(w) // 2
            add(fx, o, w)
    vo = vo[: int(total * SR)]
    fx = fx[: int(total * SR)]
    m = music(total, rng)
    # duck the music under the voice (smoothed envelope)
    env = np.abs(vo)
    k = int(0.25 * SR)
    c = np.concatenate([[0], np.cumsum(env)])
    idx = np.arange(len(env))
    env = (c[np.clip(idx + k // 2, 0, len(env))] - c[np.clip(idx - k // 2, 0, len(env))]) / k
    duck = 1 - 0.55 * np.clip(env / 0.03, 0, 1)
    fade = np.minimum(1, np.minimum(np.arange(len(vo)) / (1.0 * SR), (len(vo) - np.arange(len(vo))) / (2.5 * SR)))
    mus = m * (duck * fade)[:, None] * 0.9
    mix = mus + np.stack([vo, vo], 1) + np.stack([fx, fx], 1)
    raw = OUT / f"{fmt}-raw.wav"
    write_wav(raw, mix)
    final = OUT / f"{fmt}-mix.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", str(SR), str(final)], check=True)
    print(f"{fmt}: {total:.1f}s -> {final.name}")


if __name__ == "__main__":
    for f in sys.argv[2:] or ["landscape", "reel"]:
        main(f)
