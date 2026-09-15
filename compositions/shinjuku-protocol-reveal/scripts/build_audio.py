"""Synthesise the percussive design bed for the press-sheet trailer.

No music provider is reachable on this machine (0/5 music_generation configured;
pixabay_music is denied by the session network policy), so the bed is built from
first principles with numpy and written as WAV. It is sound design, not music:
plate impacts, roller whooshes, a riser and a dry click track, all landing on the
same 12-beat grid the composition cuts on.
"""
from __future__ import annotations
import wave
from pathlib import Path

import numpy as np

SR = 48_000
DUR = 10.0
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "audio" / "bed.wav"
OUT.parent.mkdir(parents=True, exist_ok=True)

# the cut grid, from scene_plan — every hit lands on a shot boundary
CUTS = [0.000, 0.583, 1.167, 1.708, 2.250, 3.000,
        3.583, 4.292, 4.875, 5.583, 6.292, 7.500]

rng = np.random.default_rng(0xC41)          # seeded: the render must be reproducible
n = int(SR * DUR)
t = np.arange(n) / SR
mix = np.zeros(n, dtype=np.float64)


def place(sig: np.ndarray, at: float, gain: float = 1.0) -> None:
    i = int(at * SR)
    if i >= n:
        return
    seg = sig[: n - i]
    mix[i : i + len(seg)] += seg * gain


def env(length: float, attack: float, decay: float, power: float = 2.0) -> np.ndarray:
    k = int(length * SR)
    e = np.ones(k)
    a = max(1, int(attack * SR))
    e[:a] = np.linspace(0, 1, a)
    d = max(1, int(decay * SR))
    e[-d:] = np.linspace(1, 0, d) ** power
    return e


def impact(length=0.45, f0=88.0, f1=38.0) -> np.ndarray:
    """Plate hit: a pitched-down sine thump plus a short noise transient."""
    k = int(length * SR)
    tt = np.arange(k) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 14)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(length, 0.001, length * 0.9, 2.2)
    click = rng.normal(0, 1, k) * env(length, 0.0005, 0.035, 3.0) * 0.35
    return body * 0.9 + click


def whoosh(length=0.42, bright=0.5) -> np.ndarray:
    """Roller sweep: band-passed noise whose centre sweeps upward."""
    k = int(length * SR)
    noise = rng.normal(0, 1, k)
    # one-pole sweep: cheap, deterministic, and reads as a filtered whoosh
    out = np.zeros(k)
    acc = 0.0
    for i in range(k):
        a = 0.02 + 0.55 * bright * (i / k)
        acc += a * (noise[i] - acc)
        out[i] = noise[i] - acc          # high-passed residue
    return out * env(length, length * 0.45, length * 0.5, 1.6) * 0.5


def click(length=0.05, f=2100.0) -> np.ndarray:
    k = int(length * SR)
    tt = np.arange(k) / SR
    return np.sin(2 * np.pi * f * tt) * env(length, 0.0004, length * 0.9, 3.5) * 0.18


def riser(length=1.20) -> np.ndarray:
    k = int(length * SR)
    tt = np.arange(k) / SR
    f = 180 * (2 ** (tt / length * 2.4))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    shimmer = rng.normal(0, 1, k) * 0.25
    return (tone * 0.5 + shimmer) * (np.linspace(0, 1, k) ** 2.4) * 0.5


# --- sub-bass floor: one long breath under the whole piece --------------------
floor = np.sin(2 * np.pi * 34 * t) * 0.10
floor *= np.clip(np.linspace(0.2, 1.0, n) ** 0.5, 0, 1)
floor[int(7.9 * SR):] *= np.linspace(1, 0.25, n - int(7.9 * SR))
mix += floor

# --- one impact per cut, weighted by beat importance -------------------------
WEIGHT = {0: 0.55, 1: 1.00, 2: 0.45, 3: 1.00, 4: 0.70, 5: 0.60,
          6: 0.95, 7: 0.65, 8: 0.75, 9: 0.85, 10: 0.80, 11: 1.00}
for i, c in enumerate(CUTS):
    place(impact(0.50 if WEIGHT[i] > 0.8 else 0.34), c, WEIGHT[i] * 0.85)
    place(click(), c, WEIGHT[i])

# --- misregister jitter (s03) — two dry ticks, deliberately unmusical --------
place(click(0.035, 1500), 1.250, 0.7)
place(click(0.035, 1500), 1.365, 0.7)

# --- the SNAP (s04): plate registering home ---------------------------------
place(impact(0.65, 130, 42), 1.708, 1.15)
place(whoosh(0.30, 0.9), 1.660, 0.9)

# --- roller wipes: s05 window opening, s10 roller sweep ----------------------
place(whoosh(0.46, 0.55), 2.230, 0.85)
place(whoosh(0.52, 0.75), 5.560, 0.95)

# --- triptych panels (s09): three staggered slides --------------------------
for k, off in enumerate((0.0, 0.085, 0.170)):
    place(whoosh(0.26, 0.35 + 0.15 * k), 4.875 + off, 0.5)

# --- riser into the lockup ---------------------------------------------------
place(riser(1.25), 6.28, 0.85)

# --- assembly (s11): four plates landing ------------------------------------
for k, off in enumerate((0.00, 0.28, 0.56, 0.86)):
    place(impact(0.36, 96 - k * 12, 40), 6.292 + off, 0.55 + 0.12 * k)

# --- the lockup hit + tail ---------------------------------------------------
place(impact(1.40, 150, 33), 7.500, 1.25)
place(whoosh(0.60, 0.25), 7.470, 0.7)

# --- master: soft-knee limit, then a short fade at the tail ------------------
mix = np.tanh(mix * 1.15) * 0.92
tail = int(0.35 * SR)
mix[-tail:] *= np.linspace(1, 0, tail)
peak = np.max(np.abs(mix))
mix = mix / peak * 0.89

stereo = np.stack([mix, mix], axis=1)
pcm = (stereo * 32767).astype(np.int16)
with wave.open(str(OUT), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {OUT}  {DUR}s  {SR}Hz stereo  peak={np.max(np.abs(mix)):.3f}")
