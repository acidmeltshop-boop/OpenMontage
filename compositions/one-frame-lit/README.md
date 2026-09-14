# One Frame, Lit

A 60-second narrated explainer on transmuting adversity into presence — the film-reel
metaphor, the sine wave whose trough gives the peak its height, and the compression
phase that resolves in release.

Built with the `animation` pipeline on the **HyperFrames** runtime. Every asset is
generated locally: no API keys, no stock media, no paid providers.

| | |
|---|---|
| Output | 1920×1080, 30fps, 60.000s |
| Narration | Piper `en-us-lessac-medium`, neural TTS, offline |
| Score | A-minor drone synthesized in numpy, sidechain-ducked under the voice |
| Motion | Hand-authored GSAP on one seekable paused timeline |
| Cost | $0.00 |

## Why the audio is built before the visuals

Each of the 14 narration lines is synthesized **separately** and measured, then the
visual timeline is driven off those real durations (`audio/timings.json`). Nothing is
eyeballed — every scene start is derived from when its line actually speaks. Re-running
narration with a different `length_scale` shifts the whole timing map, so regenerate
`timings.json` before touching the composition.

## Rebuild

Two assets are not committed (both fetchable, neither belongs in git):

```bash
# 1. Piper voice model — huggingface may be blocked; GitHub Releases carries it too
mkdir -p /tmp/piper-models && cd /tmp
curl -sSL -o lessac.tar.gz \
  https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz
tar -xzf lessac.tar.gz -C /tmp/piper-models

# 2. GSAP, vendored locally — the composition must not fetch at render time
mkdir -p vendor && npm pack gsap@3.14.2 && tar -xzf gsap-3.14.2.tgz
cp package/dist/gsap.min.js vendor/gsap.min.js
```

Then:

```bash
python narration.py 1.08      # synthesize lines, write audio/timings.json
python build_audio.py         # mix narration + score -> audio/master.wav
npx hyperframes lint          # must be 0 errors
npx hyperframes snapshot --frames 9   # eyeball before committing to a render
npx hyperframes render --quality high --output one-frame-lit.mp4
```

Requires `ffmpeg` on PATH and the project venv active (`piper` must resolve as a command,
or the tool registry reports `piper_tts` unavailable).

## Composition notes

Monolithic on purpose — one `index.html`, no sub-compositions. `lint` suggests splitting,
but sub-compositions introduce cross-file mount failures that `lint`/`validate`/`inspect`
cannot catch, which is a bad trade for a single 60s piece.

Two constraints shaped the code more than anything else:

- **Only `opacity`/`x`/`y`/`scale`/`rotation`/`color`/transforms are safe to animate.** The
  wave therefore reveals via a sliding opaque cover (`#wavecover`, pure `x`), not
  `strokeDashoffset`.
- **One writer per property per element.** The projector flicker lives on its own
  `#flicker` layer rather than sharing `opacity` with `#beamglow`, and the closing fade
  uses a dedicated `#fadeout` rather than animating the vignette over the last line.

`check` reports `text_occluded` on `#s11t` — a false positive. It samples at fade
boundaries where the final line is *intentionally* semi-transparent; the rendered frames
at 52s and 57s are clearly legible.
