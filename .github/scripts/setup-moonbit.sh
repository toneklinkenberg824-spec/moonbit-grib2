#!/usr/bin/env bash
# Official archive layout/bundling interface: https://cli.moonbitlang.com/install/unix.sh
set -euo pipefail
test -n "$MOON_HOME"
test -d "$RUNNER_TEMP"
test "$(uname -ms)" = "Linux x86_64"
test ! -e "$MOON_HOME/bin/moon"
version='0.10.12%2B1634b282e'
sdk="$RUNNER_TEMP/moonbit-linux-x86_64.tar.gz"
core="$RUNNER_TEMP/moonbit-core.tar.gz"
curl --fail --location --retry 3 --output "$sdk" \
  "https://cli.moonbitlang.com/binaries/$version/moonbit-linux-x86_64.tar.gz"
curl --fail --location --retry 3 --output "$core" \
  "https://cli.moonbitlang.com/cores/core-$version.tar.gz"
printf '%s  %s\n' '9bbda7d342fa39654a65c23805e5ff5a3915a26b36627a2565a6b1a99d099e01' "$sdk" | sha256sum --check
printf '%s  %s\n' '784a12ce4e204a3a98a0b704a021f747b916412efacd4dfe2f4e5c27ae183ac1' "$core" | sha256sum --check
mkdir -p "$MOON_HOME/lib"
tar -xzf "$sdk" -C "$MOON_HOME"
tar -xzf "$core" -C "$MOON_HOME/lib"
export PATH="$MOON_HOME/bin:$PATH"
moon -C "$MOON_HOME/lib/core" bundle --target js --warn-list -a
moon -C "$MOON_HOME/lib/core" bundle --target wasm-gc --warn-list -a
printf '%s\n' "$MOON_HOME/bin" >> "$GITHUB_PATH"
moon version --all
