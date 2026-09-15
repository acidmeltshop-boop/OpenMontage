# Art Direction — SHINJUKU PROTOCOL // Press Sheet

## Design read

A neo-noir crime title card built as a press sheet in motion. Cold, procedural, inked.
**The layout is violent; the man is still.** Every frame he appears in is a static plate —
all motion belongs to the sheet around him. That inversion is the whole piece: the reference
this riffs on has an athlete colliding with type, and a poster of a man holding a drink cannot
and should not do that.

## The governing conceit

The trailer is a printing press. It does not "transition" — it **prints**. Every change on
screen is a real press mechanic:

| Mechanic | Where | What it means |
|---|---|---|
| Plate drop | s02, s11 | An ink plate lands on the stock |
| Misregistration | s03 | The crimson plate is 14px out and jitters |
| Register snap | s04 | The plate finds its marks and locks |
| Roller wipe | s05, s10 | A roller passes and leaves ink behind |
| Separation flip | s06 | The image resolves into its two plates |
| Panel slide | s09 | Three printings dealt side by side |
| Halftone shimmer | s12 | The screen settling as the ink dries |

There are **no dissolves, no glitch, no shatter**. One transition family between shots: the
hard cut. All other motion happens *inside* a shot.

## Palette — two accents, never more

| Token | Hex | Role |
|---|---|---|
| Stock | `#F2EFE9` | Paper. The base state. |
| Ink | `#0B0B0C` | The key plate. |
| Crimson | `#C8102E` | The only warm accent. Lifted from the supplied posters. |
| Cyan | `#1FB6C9` | Registration artefact **only** — one beat (s08). Never decorative. |

No gradients on type. No drop shadows. No bevels.

## Typography

- **Hero:** Archivo Black, ALL CAPS, tracked tight, set large enough to bleed off-frame.
  One hero glyph per shot. It is allowed to be cropped by the frame — a poster's type often is.
- **Technical:** Roboto Mono 500/700 at 13–18px for plate labels, coordinates, sheet numbers.
- **Furniture:** Archivo 600 at 11–13px for margin micro-type.

Fonts are vendored in `fonts/` — no render-time network fetch.

## The signature device — used once

**Type-as-window:** the poster artwork is visible *only* inside the letterforms
(`background-clip: text`). It appears in exactly **one beat (s07)** and nowhere else.
It earns its weight by being scarce. This is the piece's answer to the reference's
type-as-occluder trick — done as printing rather than compositing, because no
background-removal tool is available to cut the man out.

## The furniture layer

Crop marks, colour-calibration bar, greyscale step wedge, margin micro-type, barcode and
frame counter are on screen for all 240 frames, rendered through `mix-blend-mode: difference`
so they read correctly against stock *and* against ink without ever being redrawn. This is the
layer that teaches the viewer to read "printed matter" in the first 14 frames, which is what
makes every later violation of the sheet land.

## Motion law

- Cuts land on the audio bed's transients. The bed was built to the cut grid, not fitted after.
- **One dominant move per shot.** If two things want to move, one of them is wrong.
- Easing is mechanical: `power4.out` for plates landing, `none`/stepped for misregistration
  jitter, `power2.inOut` for rollers. Nothing bounces. Nothing is elastic. Presses don't bounce.
- The final 2.5s is **dead still** except one halftone shimmer that settles over 0.4s.

## Anti-patterns (do not do these)

- Neon-cyberpunk purple/teal gradient backgrounds
- Katakana used as decoration with no meaning
- RGB-split glitch standing in for a real transition
- Full-frame stock film-grain applied as a filter
- More than one dominant move inside a single shot
- The signature device appearing in more than one beat

## Distinctness check

Could this be any other product's video? No — the conceit is bound to the fact that the source
material is three *printings* of one film, and the motion vocabulary is drawn from how those
prints are actually made. Does it reuse a look built before? No — no stock scene-type, no
registry block, no preset playbook. Every element here is authored for this piece.
