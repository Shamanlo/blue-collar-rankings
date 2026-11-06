"""Generate one voiceover WAV per line in script.json with Gemini TTS.

Usage: GEMINI_API_KEY=... python3 tts.py [out_dir]
Writes out_dir/<id>.wav (24 kHz mono). Skips lines whose WAV already exists.
"""
import base64, json, os, sys, time, urllib.request, wave, pathlib

here = pathlib.Path(__file__).resolve().parent
cfg = json.loads((here / "script.json").read_text())
out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else here / "audio")
out.mkdir(parents=True, exist_ok=True)
key = os.environ["GEMINI_API_KEY"]
url = f"https://generativelanguage.googleapis.com/v1beta/models/{cfg['model']}:generateContent"

for line in cfg["lines"]:
    dest = out / f"{line['id']}.wav"
    if dest.exists():
        continue
    body = {
        "contents": [{"parts": [{"text": f"{cfg['style']} {line['text']}"}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": cfg["voice"]}}},
        },
    }
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json", "x-goog-api-key": key})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            part = data["candidates"][0]["content"]["parts"][0]["inlineData"]
            break
        except Exception as e:  # retry transient errors
            print(f"{line['id']}: attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(2 ** (attempt + 1))
    else:
        sys.exit(f"{line['id']}: giving up")
    pcm = base64.b64decode(part["data"])
    rate = 24000
    mime = part.get("mimeType", "")
    if "rate=" in mime:
        rate = int(mime.split("rate=")[1].split(";")[0])
    with wave.open(str(dest), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
    print(f"wrote {dest} ({len(pcm) / 2 / rate:.2f}s)")
