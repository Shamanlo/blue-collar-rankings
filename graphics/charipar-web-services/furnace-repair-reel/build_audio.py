"""Stitch the voiceover lines into one track, build the caption timeline, and make a soft music bed.

Usage: python3 build_audio.py <audio_dir>
Reads <audio_dir>/l*.wav and <audio_dir>/words.json (from a transcription pass), writes:
  <audio_dir>/voice.wav     the stitched voiceover (24 kHz mono)
  <audio_dir>/music.wav     a quiet synth pad bed for the whole reel incl. the outro (48 kHz stereo)
  timeline.json (next to this script)  scene start/end times and per-word caption timings
"""
import json, re, subprocess, sys, wave, pathlib
import numpy as np

here = pathlib.Path(__file__).resolve().parent
adir = pathlib.Path(sys.argv[1])
cfg = json.loads((here / "script.json").read_text())
words = json.loads((adir / "words.json").read_text())

LEAD_IN = 0.35     # silence before the first line
GAP = 0.16         # pause between lines
OUTRO = 9.0        # seconds of outro after the last line (no voice)
SR = 24000


def speech_bounds(path, dur):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "silencedetect=noise=-42dB:d=0.12",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
    onset = ends[0] if starts and starts[0] < 0.01 and ends else 0.0
    tail = starts[-1] if starts and starts[-1] > dur - 0.6 else dur
    return onset, tail


voice = [np.zeros(int(LEAD_IN * SR), dtype=np.int16)]
t = LEAD_IN
scenes, caption_words = [], []
for line in cfg["lines"]:
    p = adir / f"{line['id']}.wav"
    with wave.open(str(p)) as w:
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    dur = len(pcm) / SR
    onset, tail = speech_bounds(p, dur)
    a, b = max(0.0, onset - 0.05), min(dur, tail + 0.1)
    clip = pcm[int(a * SR):int(b * SR)]
    voice.append(clip)
    # map transcript word times linearly onto the detected speech span
    ws = words[line["id"]]["words"]
    w0, w1 = ws[0][1], ws[-1][2]
    s0, s1 = onset - a, tail - a
    scale = (s1 - s0) / max(1e-6, (w1 - w0))
    for wd, st, en in ws:
        caption_words.append({"w": wd, "s": round(t + s0 + (st - w0) * scale, 3),
                              "e": round(t + s0 + (en - w0) * scale, 3), "line": line["id"]})
    scenes.append({"id": line["id"], "scene": line["scene"], "start": round(t, 3), "end": round(t + len(clip) / SR, 3)})
    t += len(clip) / SR
    voice.append(np.zeros(int(GAP * SR), dtype=np.int16))
    t += GAP

voice_end = t
total = round(voice_end + OUTRO, 3)
scenes.append({"id": "outro", "scene": "outro", "start": round(voice_end, 3), "end": total})
v = np.concatenate(voice)
with wave.open(str(adir / "voice.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(v.tobytes())

# --- music bed: slow warm pad, Am - F - C - G, 2 bars each at 96 bpm, with a soft pulse ---
MSR = 48000
n = int(total * MSR)
tt = np.arange(n) / MSR
bpm = 96
beat = 60 / bpm
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]  # MIDI notes
chord_len = beat * 8
out = np.zeros((n, 2))
rng = np.random.default_rng(7)
for ci in range(int(total / chord_len) + 1):
    c0 = ci * chord_len
    i0, i1 = int(c0 * MSR), min(n, int((c0 + chord_len + 1.0) * MSR))
    if i0 >= n:
        break
    seg = tt[i0:i1] - c0
    env = np.minimum(1, seg / 0.9) * np.clip((chord_len + 1.0 - seg) / 1.2, 0, 1)
    for k, note in enumerate(chords[ci % 4] + [chords[ci % 4][0] - 12]):
        f = 440 * 2 ** ((note - 69) / 12)
        for side, det in ((0, -0.12), (1, 0.12)):
            ph = rng.uniform(0, 2 * np.pi)
            wv = (np.sin(2 * np.pi * (f + det) * seg + ph) + 0.25 * np.sin(2 * np.pi * 2 * (f + det) * seg + ph)
                  + 0.1 * np.sin(2 * np.pi * 3 * (f + det) * seg))
            out[i0:i1, side] += wv * env * (0.55 if k == 3 else 0.32)
# soft kick-ish pulse on each beat
pulse = np.zeros(n)
for bi in range(int(total / beat)):
    i0 = int(bi * beat * MSR)
    L = int(0.25 * MSR)
    seg = np.arange(min(L, n - i0)) / MSR
    pulse[i0:i0 + len(seg)] += np.sin(2 * np.pi * (55 + 60 * np.exp(-seg * 30)) * seg) * np.exp(-seg * 14)
out += pulse[:, None] * 0.9
# fade in/out and normalise
fade = np.minimum(1, tt / 1.5) * np.clip((total - tt) / 2.0, 0, 1)
out *= fade[:, None]
out /= np.abs(out).max() + 1e-9
out = (out * 0.8 * 32767).astype(np.int16)
with wave.open(str(adir / "music.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(MSR); w.writeframes(out.tobytes())

(here / "timeline.json").write_text(json.dumps({"duration": total, "voiceEnd": round(voice_end, 3),
                                                "scenes": scenes, "words": caption_words}, indent=1))
print(f"voice {voice_end:.2f}s, total {total:.2f}s, {len(caption_words)} words")
