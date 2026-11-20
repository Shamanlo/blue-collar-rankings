"""Write YouTube-ready .srt captions from out/timings.json (narration and on-camera soundbites).

    python3 _engine/srt.py <project>

Writes out/<project>.srt and out/<project>-reel.srt next to the videos.
"""
import json
import re
import sys
from pathlib import Path

P = Path(sys.argv[1]).resolve()
T = json.loads((P / "out" / "timings.json").read_text())
SPEC = json.loads((P / "script.json").read_text())
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())


def punctuate(words, say):
    """Swap each timed word for the matching token from the script, which keeps its punctuation."""
    toks, j, out = say.split(), 0, []
    for t, w in words:
        for k in range(j, min(j + 4, len(toks))):
            if norm(toks[k]) == norm(w):
                out.append((t, toks[k].strip('"“”')))
                j = k + 1
                break
        else:
            out.append((t, w))
    return out


MAX_CHARS, MAX_SECS = 42, 3.2


def stamp(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def cues(scenes, fmt):
    say = {x["id"]: x["say"] for x in SPEC[fmt]}
    out = []
    for sc in scenes:
        words = [(sc["start"] + t, w) for t, w in punctuate(sc["words"], say.get(sc["id"], "")) if w.strip()]
        end_of_scene = sc["start"] + sc["dur"]
        line, t0 = [], None
        for i, (t, w) in enumerate(words):
            if t0 is None:
                t0 = t
            line.append(w)
            nxt = words[i + 1][0] if i + 1 < len(words) else None
            text = " ".join(line)
            brk = (nxt is None or len(text) + len(words[i + 1][1]) + 1 > MAX_CHARS
                   or nxt - t0 > MAX_SECS or w.endswith((".", "?", "!", ":")) or (w.endswith(",") and len(text) > 24))
            if brk:
                end = min(nxt if nxt is not None else end_of_scene - 0.3, t0 + 4.5)
                out.append((t0, max(end, t0 + 0.6), text))
                line, t0 = [], None
    return out


for fmt, suffix in (("landscape", ""), ("reel", "-reel")):
    if fmt not in T:
        continue
    lines = []
    for i, (a, b, text) in enumerate(cues(T[fmt], fmt), 1):
        lines += [str(i), f"{stamp(a)} --> {stamp(b)}", text, ""]
    f = P / "out" / f"{P.name}{suffix}.srt"
    f.write_text("\n".join(lines))
    print("wrote", f.relative_to(P.parent))
