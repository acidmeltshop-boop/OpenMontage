import json, subprocess, wave, os, sys

MODEL = "/tmp/piper-models/en-us-lessac-medium.onnx"
CONFIG = "/tmp/piper-models/en-us-lessac-medium.onnx.json"
OUT = "audio/lines"
os.makedirs(OUT, exist_ok=True)

# (id, text, gap_after_seconds)
LINES = [
    ("l01", "You think you're trapped inside this moment.", 0.25),
    ("l02", "That's the whole malfunction.", 0.55),
    ("l03", "You've mistaken a single frame for the entire reel.", 0.70),
    ("l04", "Contraction is the physics of loss. Not proof that something's wrong with you.", 0.60),
    ("l05", "The low isn't a failure. It's a coordinate.", 0.45),
    ("l06", "You cannot draw a wave with only its peaks.", 0.30),
    ("l07", "The trough is what gives the peak its height.", 0.55),
    ("l08", "The depth isn't happening to the arc. The depth is the arc.", 0.70),
    ("l09", "You are not the frame you're on. You're the awareness watching it.", 0.45),
    ("l10", "The reel keeps moving whether you grip this frame or not.", 0.70),
    ("l11", "Scarcity is a search function. It scans for not enough, and finds it. Every time.", 0.60),
    ("l12", "Ask only what's true in the three feet around your body. Breath. Weight. Sound.", 0.70),
    ("l13", "This isn't your permanent address. It's the compression phase.", 0.45),
    ("l14", "Your only job is to stop adding weight. And let it complete.", 0.0),
]

length_scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0

def dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()

timings, t = [], 0.0
for lid, text, gap in LINES:
    path = f"{OUT}/{lid}.wav"
    subprocess.run(
        ["piper", "-m", MODEL, "-c", CONFIG, "-f", path,
         "--length-scale", str(length_scale), "--sentence-silence", "0.15"],
        input=text, text=True, check=True, capture_output=True,
    )
    d = dur(path)
    timings.append({"id": lid, "text": text, "start": round(t, 3),
                    "dur": round(d, 3), "end": round(t + d, 3), "gap": gap})
    t += d + gap

json.dump({"length_scale": length_scale, "total": round(t, 3), "lines": timings},
          open("audio/timings.json", "w"), indent=2)
print(f"length_scale={length_scale}  TOTAL={t:.2f}s")
for x in timings:
    print(f"  {x['id']}  {x['start']:6.2f} -> {x['end']:6.2f}  ({x['dur']:.2f}s)  {x['text'][:52]}")
