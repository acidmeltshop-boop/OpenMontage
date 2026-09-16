# STILLWATER — "Come back to quiet."

A 30-second fictional-retreat ad cut from 13 supplied 4s clips.

## Spec

| | Planned | Actual |
|---|---|---|
| Duration | 30.00s / 720 frames @ 24fps | **30.00s / 720 frames** ✅ |
| Aspect | 16:9 | 16:9 ✅ |
| Resolution | 4K | **1280×720** ❌ source-limited |
| Audio | VO + original score + sound design | not yet built |

## Files

- `*.mp4` — the 13 source clips (4.01s each, 1280×720, 24fps, h264)
- `edit_decision_list.json` — shot-to-clip mapping, timeline and source in/out points

Renders and intermediates live in `projects/stillwater/` (gitignored, regenerable).

## Assembly

The picture-lock is assembled from `edit_decision_list.json` with the repo's
`video_trimmer` tool (`operation: concat`), which cuts each source to its
planned duration and joins them with straight cuts.

## Known continuity gaps

The generated footage does not hold to the brief's "lock her identity" and
"preserve the reference" constraints. See the notes in
`edit_decision_list.json` and the session discussion before treating the
picture-lock as final.
