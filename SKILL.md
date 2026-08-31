---
name: slopmonster
description: Turn AI-written copy into copy a human would ship. Lint for AI tells, rewrite, cleanse with a rival model, lint again. Trigger on /slopmonster, "humanize this", "de-slop this", "does this sound like AI", "fix this copy".
---

# SlopMonster

Take any draft and make it read like a person wrote it. A landing page, a README, an
email, a script. The target is not "passes a detector". Detectors are noise, and chasing them makes prose
worse. The target is the gut of a reader who has seen a thousand AI paragraphs this month.

The loop is always the same four steps, and the linter gets the first and last word,
because the linter is honest and the model is persuasive.

```
1. LINT      python3 tools/deslop.py --text "…"      score /5, exits red below 5
2. REWRITE   three passes, by hand or by model       (see below)
3. CLEANSE   a DIFFERENT model family strips tells   tools/cleanse.sh
4. RE-LINT   python3 tools/deslop.py again           ship only at 5/5
```

## Step 1 — Lint

```bash
python3 tools/deslop.py page.html              # a built page (scores visible text only)
python3 tools/deslop.py page.html --view hero  # one element by id
python3 tools/deslop.py --text "paste a draft"
python3 tools/deslop.py page.html --allow-proof  # numbers are real and evidenced
```

Regex, no opinions. Five groups, one point each: AI vocabulary, AI constructions,
punctuation cadence, rule-of-three rhythm, invented proof. Below 5/5 it exits non-zero, so
it works as a build gate. "Mostly clean" is how a page ends up sounding like every other
AI page on the internet.

Empty input fails rather than passing. A cleanse that times out leaves a zero-byte file,
and a gate that stamps that CLEAN reports slop as clean exactly when the pipeline broke.

Touching a regex means running `python3 tools/test_deslop.py`. The catalogue is matched by
word root, and the obvious stemming shortcut silently kills a dozen base words.

## Step 2 — Rewrite (three passes)

Full catalogue in `references/signs-of-ai-writing.md`. The short version:

1. **Kill the vocabulary.** `delve`, `seamless`, `robust`, `unlock`, `elevate`,
   `leverage`, `game-changing`, `journey`, `realm`… Replace with a plainer word, not a
   synonym of the same word.
2. **Kill the shapes.** `not just X, but Y` is the single loudest tell in English right
   now. Also the `rule-of-three` reflex, `em-dash` pile-ups, hedge stacks, symmetrical
   paragraphs, the closing summary nobody asked for, and a bold lead on every bullet.
3. **Put a person back in.** Removing tells leaves clean, dead copy. One specific number
   per claim. Sentence lengths that vary hard. One thing a cautious writer would have cut.
   One rough edge — a contraction, a fragment, a sentence starting with "And".

## Step 3 — Cleanse with a rival model

A model is bad at hearing its own accent. A rival model hears it instantly. So the cleanse
runs on a **different model family** than the one that wrote the draft:

| You are working in | The draft's accent | Cleanse with |
|---|---|---|
| Claude Code / Claude | Anthropic | GPT-5.6 via the codex CLI — `tools/cleanse.sh` does this |
| Codex / ChatGPT | OpenAI | Claude via `claude -p`, or set `DESLOP_WRITER=gpt` for `cleanse.sh` |
| Gemini CLI | Google | Either CLI; `cleanse.sh` picks whichever is installed |
| No CLI at all | — | `cleanse.sh` prints the prompt; paste it into the other family's chat |

```bash
tools/cleanse.sh draft.md > cleansed.md      # time-bound, exits 124 on hang
```

The instruction it carries (`prompts/cleanse.txt`): strip the tells, keep every fact,
keep the length within 10%, invent nothing, return only the copy.

## Step 4 — Re-lint

Always. A frontier model is very good at removing tells and quite capable of adding new
ones while it does. An unlinted cleanse is a coin flip.

## The one hard rule

**Never invent proof.** No user counts, no testimonials, no ratings, no `trusted by
10,000 teams` unless every one is true and you can show it. If a claim needs a number you
do not have, write `[needs number]` and move on. The linter flags number-plus-noun
patterns on purpose: a false positive costs ten seconds, a false negative is a claim you
cannot back. Specificity beats borrowed credibility anyway.

## Output format

Return the rewritten copy first, in full. Then a short `▎ what changed` list — at most
five lines, each naming the tell and the fix. Never return analysis alone. Keep the
author's meaning exactly: de-slopping is not rewriting the argument. Match the register
you were given.
