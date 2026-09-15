# SHINJUKU PROTOCOL — Press Sheet

A 10-second neo-noir character-reveal trailer. 1920×1080, 24fps, 240 frames.

Hand-authored HyperFrames composition (HTML/CSS/GSAP), `composition_mode: atelier`.
Every visual plate derives from the three posters in [`reference_posters/`](../../reference_posters).
No image, video or music provider was used — none is configured on the build machine, and
none was needed.

**Total cost: $0.00.**

| | |
|---|---|
| Pipeline | `animation` |
| Runtime | `hyperframes` 0.8.40 (locked at proposal, carried through unchanged) |
| Authoring mode | atelier — no stock scene-types, no registry blocks, no preset playbook |
| Audio | locally synthesised percussive bed, seeded RNG (`0xC41`) |
| Fonts | Archivo Black / Archivo / Roboto Mono, vendored in `fonts/` |
| GSAP | vendored in `vendor/` — the CDN is unreachable behind the session proxy |

Read [`art-direction.md`](art-direction.md) first. It states the design read, the print-mechanic
vocabulary every transition is drawn from, the palette rules, and the single signature device.

## Layout

```
index.html          the composition — 12 clips, one paused GSAP timeline
art-direction.md    the design contract
scripts/            deterministic asset derivation
  build_plates.py   crops, duotone separations, clustered-dot halftone screens
  build_audio.py    the percussive bed, built to the cut grid
artifacts/          every pipeline artifact, all schema-valid
final.mp4           the render
fonts/ vendor/      vendored dependencies (no network needed at render time)
```

## Re-rendering

From the repo root:

```bash
# 1. rebuild the derived plates and the audio bed from the source posters
python projects/shinjuku-protocol-reveal/scripts/build_plates.py
python projects/shinjuku-protocol-reveal/scripts/build_audio.py

# 2. verify before spending a render
cd projects/shinjuku-protocol-reveal/hf
npx hyperframes check .

# 3. render through the pipeline (not the CLI directly — the tool runs the
#    governance gate and the post-render self-review)
```

```python
from tools.tool_registry import registry
registry.discover()
registry._tools["video_compose"].execute({
    "operation": "render",
    "edit_decisions": ...,      # artifacts/edit_decisions.json
    "asset_manifest": ...,      # artifacts/asset_manifest.json
    "proposal_packet": ...,     # artifacts/proposal_packet.json
    "workspace_path": "projects/shinjuku-protocol-reveal/hf",
    "output_path": "projects/shinjuku-protocol-reveal/renders/final.mp4",
    "fps": 24,                  # REQUIRED — hyperframes_compose defaults to 30
    "quality": "delivery",
})
```

> **`fps` is not optional.** `data-fps="24"` on the composition root is overridden:
> `hyperframes_compose` always passes `--fps` to the CLI and defaults it to 30. Without
> `fps: 24` in the tool call the render silently comes out at 30fps.

## Why this lives here and not under `projects/`

`projects/` is gitignored because everything in it is regenerable. That is true of the plates,
the audio and the render — but not of `index.html`, `art-direction.md` or the build scripts,
which are authored source. They are kept here so the piece survives the session.
