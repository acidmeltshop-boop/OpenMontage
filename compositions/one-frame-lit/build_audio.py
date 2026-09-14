import json, wave, numpy as np, os

SR = 48000
TOTAL = 60.0
LEAD_IN = 2.6
T = json.load(open("audio/timings.json"))
n = int(TOTAL * SR)
t = np.arange(n) / SR

def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if sr != SR:  # linear resample to project rate
        a = np.interp(np.linspace(0, len(a), int(len(a) * SR / sr), endpoint=False),
                      np.arange(len(a)), a).astype(np.float32)
    return a

# ── narration track: place each measured line at its offset ──────────────
narr = np.zeros(n, dtype=np.float32)
for ln in T["lines"]:
    a = read_wav(f"audio/lines/{ln['id']}.wav")
    s = int((LEAD_IN + ln["start"]) * SR)
    e = min(s + len(a), n)
    narr[s:e] += a[: e - s]

# ── ambient pad: A-minor drone that opens up in the release tail ─────────
def swell(rate, phase=0.0, lo=0.35, hi=1.0):
    return lo + (hi - lo) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t + phase))

def voice(freq, amp, rate, phase=0.0, detune=0.0):
    v = np.sin(2 * np.pi * freq * t) + (np.sin(2 * np.pi * (freq + detune) * t) if detune else 0.0)
    return amp * v * swell(rate, phase)

pad = np.zeros(n, dtype=np.float32)
pad += voice(55.0, 0.30, 0.031, 0.0, 0.17)          # sub
pad += voice(110.0, 0.22, 0.043, 1.1, 0.23)         # root A2
pad += voice(164.81, 0.10, 0.037, 2.2, 0.15)        # E3 fifth
pad += voice(220.0, 0.075, 0.028, 0.6, 0.11)        # A3
pad += voice(261.63, 0.055, 0.024, 3.0, 0.09)       # C4 minor third
pad += voice(329.63, 0.038, 0.020, 1.7, 0.07)       # E4

# faint air / projector-room tone
rng = np.random.default_rng(7)
air = rng.standard_normal(n).astype(np.float32)
b = np.exp(-2 * np.pi * 900 / SR)                    # one-pole lowpass
for _ in range(3):
    air = np.concatenate(([0.0], air[1:] * (1 - b) + air[:-1] * b)).astype(np.float32)
pad += 0.16 * air / (np.abs(air).max() + 1e-9) * swell(0.017, 0.4, 0.25, 1.0)

# release: the tail opens (octave blooms) as narration ends — "let it complete"
rel = np.clip((t - 50.0) / 6.0, 0, 1)
pad += rel * voice(440.0, 0.030, 0.05, 0.0, 0.13)
pad += rel * voice(659.25, 0.016, 0.043, 2.4, 0.09)

# soften + shape
bb = np.exp(-2 * np.pi * 2600 / SR)
for _ in range(2):
    pad = np.concatenate(([0.0], pad[1:] * (1 - bb) + pad[:-1] * bb)).astype(np.float32)

env = np.ones(n, dtype=np.float32)
fi, fo = int(4.0 * SR), int(5.0 * SR)
env[:fi] = np.linspace(0, 1, fi) ** 1.6
env[-fo:] = np.linspace(1, 0, fo) ** 1.4
pad *= env
pad *= 0.62 + 0.38 * np.clip((t - 48.0) / 8.0, 0, 1)   # let the bed bloom under the tail

def norm(x, peak):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x

narr = norm(narr, 0.72)
pad = norm(pad, 0.135)

# duck the pad under speech
sp = np.abs(narr)
w = int(0.05 * SR)
sp = np.convolve(sp, np.ones(w) / w, mode="same")
sp = sp / (sp.max() + 1e-9)
duck = 1.0 - 0.5 * np.clip(sp * 3.2, 0, 1)
a = np.exp(-1.0 / (0.18 * SR))
sm = np.empty_like(duck); acc = 1.0
for i in range(n):
    acc = a * acc + (1 - a) * duck[i]
    sm[i] = acc

mix = np.clip(narr + pad * sm, -1.0, 1.0)
stereo = np.stack([mix, mix], axis=1)

os.makedirs("audio", exist_ok=True)
with wave.open("audio/master.wav", "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())

print(f"wrote audio/master.wav  {TOTAL}s  lead_in={LEAD_IN}s  narration_ends={LEAD_IN + T['total']:.2f}s")
for ln in T["lines"]:
    print(f"  {ln['id']}  {LEAD_IN + ln['start']:6.2f} -> {LEAD_IN + ln['end']:6.2f}  {ln['text'][:50]}")
