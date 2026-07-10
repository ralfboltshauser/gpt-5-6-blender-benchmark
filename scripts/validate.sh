#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() {
  printf 'FAIL · %s\n' "$1" >&2
  exit 1
}

count_files() {
  find "$1" -maxdepth "${2:-1}" -type f -name "$3" | wc -l | tr -d ' '
}

command -v node >/dev/null 2>&1 || fail "Node.js is required"
node --check site/app.js

model_dirs=$(find . -maxdepth 1 -mindepth 1 -type d -name 'gpt-*' | wc -l | tr -d ' ')
[[ "$model_dirs" == "15" ]] || fail "expected 15 model folders, found $model_dirs"

csv_rows=$(awk 'END { print NR - 1 }' site/assets/data/benchmark.csv)
[[ "$csv_rows" == "15" ]] || fail "expected 15 CSV rows, found $csv_rows"

web_renders=$(count_files site/assets/renders 1 '*.webp')
[[ "$web_renders" == "16" ]] || fail "expected 16 web renders including reference, found $web_renders"

scene_files=$(find site/downloads -mindepth 2 -maxdepth 2 -type f -name 'scene.blend' | wc -l | tr -d ' ')
script_files=$(find site/downloads -mindepth 2 -maxdepth 2 -type f -name 'scene.py' | wc -l | tr -d ' ')
[[ "$scene_files" == "15" ]] || fail "expected 15 normalized scenes, found $scene_files"
[[ "$script_files" == "15" ]] || fail "expected 15 normalized scripts, found $script_files"

while IFS= read -r dir; do
  blends=$(find "$dir" -maxdepth 1 -type f -name '*.blend' | wc -l | tr -d ' ')
  scripts=$(find "$dir" -maxdepth 1 -type f -name '*.py' | wc -l | tr -d ' ')
  renders=$(find "$dir" -maxdepth 1 -type f -name '*.png' ! -name 'reference.png' | wc -l | tr -d ' ')
  [[ "$blends" == "1" ]] || fail "$dir should contain exactly one final .blend"
  [[ "$scripts" == "1" ]] || fail "$dir should contain exactly one builder script"
  [[ "$renders" == "1" ]] || fail "$dir should contain exactly one final render"
done < <(find . -maxdepth 1 -mindepth 1 -type d -name 'gpt-*' | sort)

read -r total_duration total_tokens < <(
  awk -F, 'NR > 1 { duration += $5; tokens += $6 } END { print duration, tokens }' site/assets/data/benchmark.csv
)
[[ "$total_duration" == "11747554" ]] || fail "duration total changed: $total_duration"
[[ "$total_tokens" == "24684392" ]] || fail "token total changed: $total_tokens"

while IFS= read -r asset; do
  [[ -e "site/$asset" ]] || fail "missing static asset referenced by index.html: $asset"
done < <(
  grep -Eo '(src|href)="[^"]+"' site/index.html \
    | sed -E 's/^(src|href)="//; s/"$//' \
    | grep -Ev '^(#|https?://)' \
    | sort -u
)

while IFS= read -r slug; do
  [[ -s "site/assets/renders/$slug.webp" ]] || fail "missing web render for $slug"
  [[ -s "site/downloads/$slug/scene.blend" ]] || fail "missing normalized scene for $slug"
  [[ -s "site/downloads/$slug/scene.py" ]] || fail "missing normalized script for $slug"
done < <(grep -Eo 'slug: "[^"]+"' site/app.js | cut -d '"' -f 2)

grep -q 'https://blender-bench.ralfboltshauser.com/' site/index.html || fail "live canonical URL missing"
grep -q 'https://github.com/ralfboltshauser/gpt-5-6-blender-benchmark' site/index.html || fail "GitHub URL missing"
grep -q 'https://www.linkedin.com/in/ralfboltshauser/' site/index.html || fail "LinkedIn URL missing"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git ls-files | grep -Eq '(^|/)(\.vercel|__pycache__)(/|$)|\.blend1$|social-copy\.md$'; then
    fail "private, transient, backup, or posting-instruction files are tracked"
  fi
fi

printf 'PASS · 15 runs · 16 web renders · 30 normalized source artifacts · audited totals match\n'
