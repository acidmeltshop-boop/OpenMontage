import json, subprocess, wave, os, sys

MODEL = "/tmp/piper-models/en-us-lessac-medium.onnx"
CONFIG = "/tmp/piper-models/en-us-lessac-medium.onnx.json"
OUT = "audio/lines"
os.makedirs(OUT, exist_ok=True)

# (id, text, gap_after_seconds)
LINES = [
    ("l01", "You've been manifesting for two years.", 0.28),
    ("l02", "Vision board. Morning routine. A folder full of screenshots.", 0.55),
    ("l03", "What you don't have is the thing.", 0.70),
    ("l04", "Here's the uncomfortable part. Manifestation works.", 0.50),
    ("l05", "Attention really does shape outcome. Which is exactly why they sell it to you.", 0.55),
    ("l06", "Every scroll is a vision board somebody else built.", 0.55),
    ("l07", "A thousand lives a day. None of them yours.", 0.70),
    ("l08", "You're not manifesting. You're being manifested through.", 0.70),
    ("l09", "Because almost arriving feels better than arriving.", 0.45),
    ("l10", "So the feed keeps you almost there. Forever.", 0.70),
    ("l11", "A wish and a plan differ by one thing. A cost.", 0.55),
    ("l12", "Hours. Discomfort. Something you give up.", 0.60),
    ("l13", "Name the price and it stops being manifestation. It starts being a life.", 0.70),
    ("l14", "You can visualize the bus all day. It still only stops if you're standing there.", 0.0),
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
         "--length-scale", str(length_scale), "--sentence-silence", "0.12"],
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
    print(f"  {x['id']}  {x['start']:6.2f} -> {x['end']:6.2f}  ({x['dur']:.2f}s)  {x['text'][:50]}")
