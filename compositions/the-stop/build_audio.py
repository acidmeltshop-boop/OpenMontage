import json, wave, numpy as np, os

SR = 48000
TOTAL = 60.0
LEAD_IN = 2.0
TURN = 48.0          # the mechanical bed gates off here — "name the price"
T = json.load(open("audio/timings.json"))
n = int(TOTAL * SR)
t = np.arange(n) / SR

def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    if sr != SR:
        a = np.interp(np.linspace(0, len(a), int(len(a) * SR / sr), endpoint=False),
                      np.arange(len(a)), a).astype(np.float32)
    return a

# ── narration ────────────────────────────────────────────────────────────
narr = np.zeros(n, dtype=np.float32)
for ln in T["lines"]:
    a = read_wav(f"audio/lines/{ln['id']}.wav")
    s = int((LEAD_IN + ln["start"]) * SR)
    e = min(s + len(a), n)
    narr[s:e] += a[: e - s]

rng = np.random.default_rng(11)

# tension curve: creeps in from the hook, peaks at "almost there, forever",
# then is cut — not faded — at the turn.
tension = np.clip((t - 6.0) / 34.0, 0, 1) ** 1.5
gate = np.clip((TURN + 0.35 - t) / 0.35, 0, 1)        # hard-ish cut at TURN
mech = tension * gate

# ── mechanical bed: a clock that speeds up ───────────────────────────────
bed = np.zeros(n, dtype=np.float32)
bpm0, bpm1 = 84.0, 132.0
phase = np.cumsum((bpm0 + (bpm1 - bpm0) * tension) / 60.0) / SR
beat = np.floor(phase)
frac = phase - beat

# low pulse on the beat
env_pulse = np.exp(-frac * 26.0)
bed += 0.5 * np.sin(2 * np.pi * 52.0 * t) * env_pulse

# mechanical tick on the offbeat
off = np.abs(frac - 0.5) < 0.02
tick = rng.standard_normal(n).astype(np.float32) * off
b = np.exp(-2 * np.pi * 5200 / SR)
tick = np.concatenate(([0.0], tick[1:] * (1 - b) + tick[:-1] * b)).astype(np.float32)
bed += 0.35 * tick

# unease drone — a tritone against the root, the sound of something not resolving
bed += 0.16 * np.sin(2 * np.pi * 104.0 * t) * (0.4 + 0.6 * tension)
bed += 0.10 * np.sin(2 * np.pi * 146.8 * t) * tension          # D above A = tritone-ish tension
bed += 0.05 * np.sin(2 * np.pi * 207.6 * t) * tension ** 2

bed *= mech

# ── the turn: mechanical stops, warmth opens ─────────────────────────────
rel = np.clip((t - TURN) / 5.0, 0, 1)
warm = np.zeros(n, dtype=np.float32)
for f, a, r in ((110.0, 0.30, 0.021), (164.8, 0.16, 0.017), (220.0, 0.10, 0.013), (329.6, 0.05, 0.011)):
    warm += a * np.sin(2 * np.pi * f * t) * (0.55 + 0.45 * np.sin(2 * np.pi * r * t))
warm *= rel
# let it breathe out at the very end
warm *= np.clip((TOTAL - t) / 4.0, 0, 1) ** 0.6

score = bed + warm
bb = np.exp(-2 * np.pi * 3000 / SR)
for _ in range(2):
    score = np.concatenate(([0.0], score[1:] * (1 - bb) + score[:-1] * bb)).astype(np.float32)

def norm(x, peak):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x

narr = norm(narr, 0.74)
score = norm(score, 0.17)

# duck the score under speech
sp = np.abs(narr)
w = int(0.05 * SR)
sp = np.convolve(sp, np.ones(w) / w, mode="same")
sp = sp / (sp.max() + 1e-9)
duck = 1.0 - 0.55 * np.clip(sp * 3.4, 0, 1)
a = np.exp(-1.0 / (0.16 * SR))
sm = np.empty_like(duck); acc = 1.0
for i in range(n):
    acc = a * acc + (1 - a) * duck[i]
    sm[i] = acc

mix = np.clip(narr + score * sm, -1.0, 1.0)
stereo = np.stack([mix, mix], axis=1)

with wave.open("audio/master.wav", "w") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())

print(f"master.wav  {TOTAL}s  lead_in={LEAD_IN}  narration_ends={LEAD_IN + T['total']:.2f}  turn={TURN}")
for ln in T["lines"]:
    print(f"  {ln['id']}  {LEAD_IN + ln['start']:6.2f} -> {LEAD_IN + ln['end']:6.2f}  {ln['text'][:46]}")
