#!/usr/bin/env bash
# The model cleanse — a second model strips the tells the first one wrote.
#
# The rule: the cleanse runs on a DIFFERENT model family than the one that wrote
# the draft. A model is bad at hearing its own accent. A rival hears it instantly.
#
#   ./cleanse.sh draft.md                # cleanse a file
#   cat draft.md | ./cleanse.sh -        # cleanse stdin
#   TIMEOUT=240 ./cleanse.sh draft.md    # longer bound for a long document
#
# Routing, in order:
#   1. codex CLI found  -> GPT-5.6 pass via `codex exec` (you are in Claude Code / Gemini)
#   2. no codex, claude CLI found AND DESLOP_WRITER=gpt -> Claude pass (you are in Codex)
#   3. neither          -> prints the prompt so you can paste it into ChatGPT yourself
#
# If you are ALREADY inside Codex/ChatGPT: you do not need this script. The GPT
# family is the one you are talking to. Paste prompts/cleanse.txt plus your draft.
#
# Always exits 124 on timeout. ALWAYS re-lint the output:
#   python3 tools/deslop.py --text "$(cat cleansed.md)"
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$HERE/../prompts/cleanse.txt"
TIMEOUT="${TIMEOUT:-180}"

if [ "${1:-}" = "-" ] || [ $# -eq 0 ]; then
  DRAFT="$(cat)"
else
  # Without this, a typo'd filename sent an EMPTY draft to a paid model call and
  # wrote the reply into your output file at exit 0.
  [ -f "$1" ] && [ -r "$1" ] || { echo "cleanse: cannot read $1" >&2; exit 66; }
  DRAFT="$(cat "$1")"
fi
[ -n "$(printf '%s' "$DRAFT" | tr -d '[:space:]')" ] || {
  echo "cleanse: draft is empty, nothing to cleanse" >&2; exit 66; }

FULL="$(cat "$PROMPT_FILE")

$DRAFT"

find_bin() { command -v "$1" 2>/dev/null || { [ -x "$HOME/.local/bin/$1" ] && echo "$HOME/.local/bin/$1"; }; }

CODEX="$(find_bin codex || true)"
CLAUDE="$(find_bin claude || true)"

run_bounded() {  # run_bounded <cmd...>  — macOS has no `timeout`, so we roll one
  OUT="$(mktemp)"; trap 'rm -f "$OUT"' RETURN
  "$@" >"$OUT" 2>&1 </dev/null &
  PID=$!; WAITED=0
  while kill -0 "$PID" 2>/dev/null; do
    if [ "$WAITED" -ge "$TIMEOUT" ]; then
      kill -9 "$PID" 2>/dev/null; wait "$PID" 2>/dev/null
      echo "deslop: cleanse timed out after ${TIMEOUT}s" >&2; return 124
    fi
    sleep 2; WAITED=$((WAITED + 2))
  done
  wait "$PID"; RC=$?; cat "$OUT"; return $RC
}

if [ -n "$CODEX" ] && [ "${DESLOP_WRITER:-claude}" != "gpt" ]; then
  # Claude (or Gemini) wrote the draft -> GPT-5.6 cleanses it.
  # --skip-git-repo-check: copy lives in plain folders. Sandbox read-only: this
  # is a text transform, it has no business writing files.
  RAW="$(run_bounded "$CODEX" exec --skip-git-repo-check --sandbox read-only "$FULL")" || exit $?
  # codex wraps the answer in banners; the answer sits between the last bare
  # `codex` line and `tokens used`.
  #
  # Test the EXTRACTION, not the first line. Branching on `read -r first` meant an
  # answer that opened with a blank line fell through to the raw transcript —
  # banner, session id, the whole prompt file — written straight into your output.
  # `read` also strips leading whitespace, which breaks the "preserve markdown
  # structure exactly" instruction the prompt file gives.
  BODY="$(printf '%s\n' "$RAW" | awk '$0=="codex"{buf="";on=1;next} $0=="tokens used"{on=0;next} on{buf=buf $0 "\n"} END{printf "%s", buf}')"
  if [ -n "$(printf '%s' "$BODY" | tr -d '[:space:]')" ]; then
    printf '%s\n' "$BODY"
  else
    printf '%s\n' "$RAW"
  fi
elif [ -n "$CLAUDE" ] && [ "${DESLOP_WRITER:-claude}" = "gpt" ]; then
  # GPT wrote the draft -> Claude cleanses it.
  run_bounded "$CLAUDE" -p "$FULL"
else
  # Reached when the only CLI available is the same family that wrote the draft.
  # Running that would be a model marking its own homework, which is the one
  # thing this script exists to prevent. Print the prompt instead.
  echo "cleanse: no rival-family CLI found (a Claude draft needs codex, a GPT" >&2
  echo "draft needs claude). Paste the block below into the other family's chat:" >&2
  echo >&2
  printf '%s\n' "$FULL"
  exit 127
fi
