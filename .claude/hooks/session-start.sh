#!/bin/bash
# Rebuilds the OpenMontage toolchain in Claude Code on the web, where every
# session starts from a fresh container. Idempotent: the expensive steps are
# skipped once the container state is cached.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

VOICE_DIR="$HOME/.cache/openmontage/piper"
VOICE_ONNX="$VOICE_DIR/en-us-lessac-medium.onnx"

# ffmpeg — nearly every tool in the registry depends on it, and `make setup`
# does not install it. Without it the HyperFrames runtime reports unavailable.
if ! command -v ffmpeg >/dev/null 2>&1; then
  apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg
fi

# Python venv + requirements + remotion-composer npm deps + piper-tts
if [ ! -x .venv/bin/python ]; then
  make setup
fi

# `make setup` installs runtime deps only, so `make test` would fail on a fresh
# container. requirements-dev.txt adds pytest and pulls in requirements.txt.
if ! .venv/bin/python -c "import pytest" >/dev/null 2>&1; then
  .venv/bin/python -m pip install -q -r requirements-dev.txt
fi

# Piper voice model. The usual source (huggingface.co) is refused by the
# sandbox network policy; the same voice ships as a GitHub release asset.
if [ ! -f "$VOICE_ONNX" ]; then
  mkdir -p "$VOICE_DIR"
  curl -fsSL --retry 3 -o /tmp/piper-voice.tar.gz \
    https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz
  tar -xzf /tmp/piper-voice.tar.gz -C "$VOICE_DIR"
  rm -f /tmp/piper-voice.tar.gz
fi

# The tool registry probes for `piper` as a command, not as an importable
# module — without .venv/bin on PATH it reports piper_tts unavailable and the
# free narration path silently disappears.
{
  echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\""
  echo "export PIPER_VOICE_ONNX=\"$VOICE_ONNX\""
  echo "export PIPER_VOICE_CONFIG=\"$VOICE_ONNX.json\""
  echo "export HYPERFRAMES_SKIP_SKILLS=1"
} >> "$CLAUDE_ENV_FILE"
