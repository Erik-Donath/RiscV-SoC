#!/bin/sh
# Small helper to set up environment for building inside the repo or container
# Usage: source ./env.sh

# Ensure GUI-less Qt
export QT_QPA_PLATFORM=offscreen

# Add local Gowin IDE binaries to PATH
export PATH="$(pwd)/IDE/bin:$PATH"

# Make sure the Gowin binaries are executable (when files are present but lack x-bit)
if [ -d "$(pwd)/IDE/bin" ]; then
  echo "Setting execute permission on files in $(pwd)/IDE/bin"
  find "$(pwd)/IDE/bin" -maxdepth 1 -type f -exec chmod a+x '{}' \; 2>/dev/null || true
fi

echo "QT_QPA_PLATFORM=$QT_QPA_PLATFORM"
echo "Gowin on PATH: $(command -v GowinSynthesis || command -v gw_ide || echo 'not found')"
