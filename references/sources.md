# Where this comes from

Nothing here is invented. Every part of the system traces to a named source.

## The canonical document

**Wikipedia: "Signs of AI writing"** — `en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing`
Maintained by WikiProject AI Cleanup: the people who remove AI text from Wikipedia for a
living. It is the closest thing to a peer-reviewed catalogue of the tells, it updates
continuously, and it is free. Read it before trusting any tool that claims to humanize.

## The open-source humanizers (all MIT)

The linter and the catalogue stand on the shoulders of the leading open-source
humanizers:

| Repo | What it is | What this skill takes from it |
|---|---|---|
| [`blader/humanizer`](https://github.com/blader/humanizer) | Agent skill built directly on the Wikipedia catalogue. Detects inflated symbolism, promotional language, vague attribution, em-dash overuse, rule-of-three, filler. Never invents facts. | The detection taxonomy. The closest thing to a reference implementation. |
| [`harshaneel/humanize`](https://github.com/harshaneel/humanize) | Two LLM-agnostic skills built on nine levers, 50+ peer-reviewed sources, 2024–2026 detection literature. | The research trail, and the em-dash finding: models use them at roughly 3–5× a human rate. |
| [`lguz/humanize-writing-skill`](https://github.com/lguz/humanize-writing-skill) | Three passes — kill the vocabulary, break the structures, add human texture. Banned words in tiers, 10 structural patterns, a 14-point checklist. | The three-pass shape and the tiering of banned words. |
| [`haidrrrry/humanize-ai-writing`](https://github.com/haidrrrry/humanize-ai-writing) | Free system prompt / skill. Bans the vocabulary and the shapes, model-agnostic. | The drop-in-prompt fallback when you cannot install anything. |

**Deliberately excluded:** the detector-bypass repos (StealthHumanizer and its clones).
They optimise for Turnitin rather than for a reader, and the prose measurably gets worse.
A detector score is not the deliverable, and "passes AI detection" is not a claim this
skill will ever make.

## The copywriting principles

- **Steve Krug**, *Don't Make Me Think* (2000) — principle 1.
- **Daniel Priestley** — pitch order: problem and insight before product. Principle 2.
- **Alex Hormozi** — the offer-side version of the same argument: named pain, checkable
  specificity, proof you actually own. Principles 2, 3 and the never-invent-proof rule
  rhyme with his playbook.
- **The category benchmark**: before rewriting a page, read the five best live pages in
  its category and quote their headlines verbatim. The bar is what the reader has already
  seen, not what sounds nice in isolation.

## The cleanse model

The reference cleanse pass is **GPT-5.6** — a frontier model from a *different family*
than the (usually Claude) model that wrote the draft. Different families have different
accents, and a model is poor at hearing its own. The pass is never trusted without the
linter on both sides.
