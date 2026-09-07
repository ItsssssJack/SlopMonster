#!/usr/bin/env bash
# Regression tests for the copy/notes split in cleanse.sh.
#
# The split is what keeps the model's change notes out of cleansed.md. Without it
# step 4 re-lints the notes as if they were prose and reports CLEAN, which is the
# gate lying at the one moment you are relying on it.
#
# Sources emit_copy out of cleanse.sh rather than reimplementing it, so this test
# fails if the real function drifts. No model calls, so it runs in CI.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
eval "$(sed -n "/^NOTES_SENTINEL=/,/^}$/p" "$HERE/cleanse.sh")"

fail=0
check() {  # check <name> <condition-result>
  if [ "$2" = "0" ]; then printf '  ok    %s\n' "$1"
  else printf '  FAIL  %s\n' "$1"; fail=1; fi
}

# ── the ordinary reply ──────────────────────────────────────────────────────
out="$(printf 'Line one.\nLine two.\n\n%s\n- killed a tell\n' "$NOTES_SENTINEL" | emit_copy 2>/dev/null)"
[ "$out" = "$(printf 'Line one.\nLine two.')" ]; check 'copy is the text above the sentinel' $?
err="$(printf 'Copy.\n\n%s\n- killed a tell\n' "$NOTES_SENTINEL" | emit_copy 2>&1 >/dev/null)"
case "$err" in *'killed a tell'*) check 'notes go to stderr' 0;; *) check 'notes go to stderr' 1;; esac
case "$out" in *'killed a tell'*) check 'notes stay OUT of stdout' 1;; *) check 'notes stay OUT of stdout' 0;; esac

# ── a draft that legitimately contains --- ──────────────────────────────────
# The old separator was a bare `---`, which is both a markdown rule and a YAML
# frontmatter delimiter, so splitting on it truncated any draft containing one.
body="$(printf 'Intro.\n\n---\n\nAfter the rule.\nFinal line.\n\n%s\n- a note\n' "$NOTES_SENTINEL" | emit_copy 2>/dev/null)"
case "$body" in *'Final line.'*) check 'copy past a --- survives' 0;; *) check 'copy past a --- survives' 1;; esac
case "$body" in *'---'*) check 'the --- itself is preserved' 0;; *) check 'the --- itself is preserved' 1;; esac
case "$body" in *'a note'*) check 'notes not leaked past a ---' 1;; *) check 'notes not leaked past a ---' 0;; esac

# ── no sentinel: fail OPEN, never eat the copy ──────────────────────────────
out="$(printf 'Only copy.\nSecond line.\n' | emit_copy 2>/dev/null)"
case "$out" in *'Second line.'*) check 'missing sentinel keeps all copy' 0;; *) check 'missing sentinel keeps all copy' 1;; esac
err="$(printf 'Only copy.\n' | emit_copy 2>&1 >/dev/null)"
case "$err" in *WARNING*) check 'missing sentinel warns loudly' 0;; *) check 'missing sentinel warns loudly' 1;; esac

# ── sentinel with nothing after it ──────────────────────────────────────────
err="$(printf 'Copy only.\n\n%s\n' "$NOTES_SENTINEL" | emit_copy 2>&1 >/dev/null)"
[ -z "$err" ]; check 'empty notes print nothing to stderr' $?

# ── the blank lines before the sentinel are not published ───────────────────
# The model separates the sentinel from the copy with a blank line. Without the
# trim, every cleansed file ends in trailing whitespace.
# Asserted through a FILE, not "$(...)": command substitution strips trailing
# newlines, so a $()-based check cannot see this bug at all and passes either way.
tmp="$(mktemp)"
printf 'Copy ends here.\n\n\n%s\n- a note\n' "$NOTES_SENTINEL" | emit_copy 2>/dev/null >"$tmp"
[ "$(wc -c <"$tmp" | tr -d ' ')" = "16" ]; check 'blank lines before the sentinel are trimmed' $?
rm -f "$tmp"

# ── the sentinel must not match when quoted inside prose ────────────────────
out="$(printf 'We use the `%s` marker.\nStill copy.\n' "$NOTES_SENTINEL" | emit_copy 2>/dev/null)"
case "$out" in *'Still copy.'*) check 'sentinel inside a line is not a split point' 0;; *) check 'sentinel inside a line is not a split point' 1;; esac

[ "$fail" = "0" ] && echo "all cleanse tests passed" || { echo "cleanse tests FAILED"; exit 1; }
