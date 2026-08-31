# SlopMonster

![The five SlopMonster mascots in a line-up, one for each rule it scores you on](docs/img/hero.png)

**Turn AI-written copy into copy a human would ship.**

AI writing has a smell. `delve`, `seamless`, `unlock`, `it's not just a tool, it's a
journey`. Readers catch it now, and a page that smells of it is a page they stop
trusting.

Most tools that fix this are built on the same public research. This one adds the two
things the others skip.

**It scores your copy out of 5 and it can fail your build.** No opinions, no vibes, just
patterns. Developers call this a linter. Everyone else can call it a checker that will
not let you ship.

**A rival model does the cleaning.** If Claude wrote the draft, GPT cleans it. A model
cannot hear its own accent, the same way you cannot hear yours.

Works on landing pages, READMEs, emails and scripts. Anything a person is going to read
and judge.

## The loop

```
1. SCORE     tools/deslop.py     marks it out of 5, exits red below 5. Patterns, no opinions.
2. REWRITE   three passes        kill the vocabulary → kill the shapes → put a person back in
3. CLEANSE   tools/cleanse.sh    a different model family strips the tells the first one wrote
4. RESCORE   tools/deslop.py     ship only at 5/5
```

The scorer gets the first word and the last word, because the scorer is honest and the
model is persuasive. "Mostly clean" is how a page ends up sounding like every other AI page on
the internet.

## Receipts, not claims

A real run on seven verbatim sentences of Jasper.ai's live homepage (29 Aug 2026):

| | score |
|---|---|
| Their copy, as fetched | **3/5** — `unlock`, `empower`, four rule-of-three lists |
| After one pass through this loop | **5/5** — meaning intact, length within 10%, nothing invented |

Every command and its exact output: [`examples/jasper-live-run.md`](examples/jasper-live-run.md).
Their copy is quoted for criticism and remains theirs; the MIT licence below covers this
repo's own code and prose.

## Quick start

```bash
git clone https://github.com/ItsssssJack/SlopMonster && cd SlopMonster

# score anything
python3 tools/deslop.py --text "It's not just a tool, it's a game-changing journey."
# → score 3/5, names both tells, exits 1

# score a built page (reads only what a visitor can SEE)
python3 tools/deslop.py index.html

# score a markdown file (skips code spans, fenced blocks and struck-through text)
python3 tools/deslop.py README.md

# cleanse a draft with a rival model, then re-score
tools/cleanse.sh draft.md > cleansed.md
python3 tools/deslop.py --text "$(cat cleansed.md)"

# your numbers are real and you can evidence them? stop the proof rule blocking the build
python3 tools/deslop.py index.html --allow-proof

# changed a regex? this is what catches a silently half-blind catalogue
python3 tools/test_deslop.py
```

No dependencies. The scorer is stdlib Python. The cleanse script needs one AI CLI
(`codex` or `claude`), or neither, in which case it prints the prompt for you to paste.
`.github/workflows/slop.yml` is the build gate, ready to copy into your own repo.

### Install as an agent skill

**Claude Code:** copy this folder to `~/.claude/skills/slopmonster/`, then say `/slopmonster` or
"de-slop this". **Codex / other agents:** point the agent at `SKILL.md` — it is
plain-markdown instructions, nothing Claude-specific.

## The cleanse is model-aware

The rule: the cleanse runs on a **different model family** than the one that wrote the
draft. Different families have different accents, and a model is poor at hearing its own.

| You work in | Draft's accent | `cleanse.sh` does |
|---|---|---|
| Claude Code | Anthropic | calls **GPT-5.6** via your `codex` CLI, time-bound, read-only sandbox |
| Codex / ChatGPT | OpenAI | set `DESLOP_WRITER=gpt` and it calls **Claude** via `claude -p` |
| Gemini CLI | Google | whichever rival CLI is installed |
| no rival CLI | n/a | prints the full prompt to paste into the other family's chat |

It refuses to route a draft back to its own family. A model marking its own homework is
the one thing this step exists to prevent.

Then it re-lints, always: a frontier model is very good at removing tells and quite
capable of adding new ones while it does.

## What the scorer hunts

Five groups. Trip one and you lose a point. Below 5/5 the command exits red, so a build can
stop on it.

Four groups strip the AI accent. The fifth asks whether the line sells anything.

Every before and after below is a real line from the Ridgeline Roofing build. Struck
through is what the first draft said. Bold is what shipped. The full record:
[`examples/ridgeline-roofing.md`](examples/ridgeline-roofing.md).

Every specimen on this page sits in `code formatting` or is struck through. That is not
decoration. A literal is not copy, so `deslop.py` skips both when it reads a `.md` file,
which is how this README passes the scorer it documents.

![Rule 1, AI vocabulary: delve, leverage, seamless, unlock](docs/img/rule-1-vocab.png)

**1. AI vocabulary.** Words that turn up far more in AI writing than in human writing.

There are two lists and they work differently.

The first list is matched by root. So `elevate` also catches `elevates`, `elevated` and
`elevating`. This matters more than it sounds. Sales pages are written in the third person.
`Acme elevates your workflow` is the commonest form of the word, and exact matching
walked straight past it.

The second list holds words that have an honest everyday meaning too. `crafted`, `harness`,
`landscape`, `journey`. Those are matched word for word instead. So "we craft furniture by
hand" stays clean, and only the marketing use gets caught.

The fix is a plainer word. Not a posher synonym for the same idea.

> ~~We leverage industry-leading materials to deliver unparalleled protection.~~
> **We source materials from manufacturers who test for wind, hail and sun.**
> `leverage`, `deliver`, `unparalleled`. Every one of them means nothing and costs a line.

![Rule 2, AI constructions: "not just a tool, it's a journey"](docs/img/rule-2-phrases.png)

**2. AI constructions.** This group catches sentence shapes, not single words.

A shape is a pattern you can fill with anything. `not just X, but Y` is the loudest one in
English right now. Once you see it you cannot stop seeing it.

There are 17 shapes in the list. Things like `that's where X comes in`, `say goodbye to`
and `whether you're X or Y`, stacked hedges such as `could potentially`, and questions
the writer then answers themselves.

Both the short and long forms are checked, "it's" and "it is". Formal register is not a
clever disguise. It is the default thing a model writes.

Shapes are worth more than words, because a page can pass a vocabulary check and still read
like a machine wrote it.

> ~~Not just a roof, but peace of mind.~~
> **A written scope and a fixed number before anyone climbs a ladder.**
> The shape promises a reveal, then hands you an abstraction.

![Rule 3, punctuation cadence: two em dashes in one sentence](docs/img/rule-3-punctuation.png)

**3. Punctuation cadence.** Two em dashes inside one sentence.

One dash in a paragraph is punctuation. Three is a tic. Models reach for them at roughly
three to five times the human rate.

The check only looks inside a 220 character window, and that limit is doing real work.
Interface text has no full stops. Nav items, buttons and labels all run together, so a
naive sentence split treats a whole page as one sentence and the rule then fires on
everything. A scorer that cries wolf gets switched off, so the window stays.

Semicolons are counted too, but only past a floor of three, scaled to the length of the
page. Two semicolons in a long technical document is a style, not a tell.

> ~~Our team — trained, certified and local — is ready to help.~~
> **Thirty-eight on the crew, factory-trained for every material we install.**
> The dashes were hiding the fact that the sentence had no information in it.

![Rule 4, rule-of-three rhythm: "faster, smarter, and better"](docs/img/rule-4-rhythm.png)

**4. Rule-of-three rhythm.** Three items in a row. `faster, smarter, and better`.

Three adjectives is a rhythm, not an argument. One tricolon is rhetoric. Three of them on a
page is a machine. A tricolon is just the posh name for a three-item list.

This check is deliberately narrow, and only two shapes fire it. With the Oxford comma it
needs three single words. Without it, the third item has to be a short phrase that ends the
clause.

The narrowness is the point. "Inspection, repair and replacement for homes" is three real
things a roofer does. Flagging that would be crying wolf, and the next person would turn
the scorer off.

> ~~Trusted, reliable and built to last.~~
> **Six nails per shingle, every shingle.**
> One specification beats three adjectives every time. Nobody invents a line like that,
> because invented copy does not know it.

![Rule 5, sales and marketing: the rewrite built on Krug, Priestley and Hormozi](docs/img/rule-5-conversion.png)

**5. Sales & marketing.** The first four rules get the robot out. This one asks the harder
question. Does the line sell anything?

Clean copy that says nothing is still a dead page. Two things run here.

**The hard rule: never invent proof.** No customer counts, no testimonials, no ratings the
business has not earned. The scorer flags any number sitting next to a people-noun, like
`10,000+ happy users`. It is deliberately trigger-happy. A false alarm costs you ten
seconds. A miss puts a claim on your site that you cannot back. If your number is real and
you can evidence it, `--allow-proof` drops it to a warning and still prints the hits.

Fake proof is a sales failure before it is a writing failure. Nobody buys from a page they
have caught lying.

> ~~Loved by 10,000+ happy homeowners.~~
> **Project names and photography are placeholders. Swap in your own jobs before this goes live.**
> Say the slot is empty. It reads as confidence, not weakness.

> ~~The area's most trusted roofing experts.~~
> **Roofing, and only roofing, since 2001.**
> "Most trusted" cannot be checked, so the reader discounts it. A date cannot be argued with.

**Where the lines come from.** Four sources. If a sentence cannot name its source, it does
not go on the page.

1. **What the trade actually does.** The strongest source by a mile. "Six nails per
   shingle" is a real specification with a real failure mode behind it.
2. **What the customer already fears.** That the price will move. That the yard will be
   wrecked. That they are being sold a whole roof for a flashing problem.
3. **What the competition will not say.** Refusals travel further than promises. "We do not
   do overlays" positions you and disqualifies the wrong customer in one line.
4. **The lines that were already good.** "From first call to final nail" arrived written in
   the wireframe and beat every rewrite. It stayed.

**The named work behind the rewrite:**

| Who | What this takes |
|---|---|
| **Steve Krug**, *Don't Make Me Think* (2000) | every line the reader has to decode is a line they skip |
| **Daniel Priestley**, pitch order | open on the problem and the insight, never the product |
| **Alex Hormozi**, the offer side | named pain, checkable specificity, proof you actually own |

Those three plus the category benchmark become five working principles, each with a real
before and after: [`references/principles.md`](references/principles.md).

## What goes in the tells' place

Clean is not the same as good. Five principles decide what the line says instead —
Krug's *Don't Make Me Think*, Priestley's problem-first pitch order, and the
specificity-over-superlatives argument Hormozi makes from the offer side. Each with a
real before/after: [`references/principles.md`](references/principles.md).

## A full worked example

The Ridgeline Roofing build: a Lorem-ipsum wireframe to a shipped site, with every
headline's before → after, the six tells caught in first drafts, and the verify-or-mark
pass on every number. This is the file that teaches:
[`examples/ridgeline-roofing.md`](examples/ridgeline-roofing.md).

> ~~The area's most trusted roofing experts.~~
> **Roofing, and only roofing, since 2001.**
> "Most trusted" is unfalsifiable, so the reader discounts it entirely. A date cannot be argued with.

## The one hard rule

**Never invent proof.** No user counts, no testimonials, no ratings you have not earned.
If a claim needs a number you do not have, write `[needs number]` and move on. The lift
from a fabricated number is smaller than the lift from real specificity, and it is the
one mistake with no route back.

And this skill will never claim to "beat AI detectors". Detectors are noise. The target
is a human reader's gut.

This file passes its own scorer. `python3 tools/deslop.py README.md` scores **5/5**, and
it is the same catalogue and the same regexes that score your landing page. Nothing was
softened to get there. The specimens are marked as literals, in `code` or struck through,
and the prose around them had to be written clean like anything else.

## What this is built on

All sources named in [`references/sources.md`](references/sources.md):
Wikipedia's *Signs of AI writing* (WikiProject AI Cleanup) as the canonical catalogue,
plus four MIT-licensed open-source humanizers: `blader/humanizer`,
`harshaneel/humanize`, `lguz/humanize-writing-skill`, `haidrrrry/humanize-ai-writing`.
The rewrite principles come from Krug, Priestley and Hormozi. Detector-bypass repos are
deliberately excluded.

## Repo map

```
SKILL.md                            the agent skill — the whole loop as instructions
tools/deslop.py                     the scorer. stdlib, no deps, exits red below 5/5
tools/test_deslop.py                regression suite. run it after touching any regex
tools/cleanse.sh                    rival-model cleanse, auto-routed, time-bound
.github/workflows/slop.yml          the build gate, ready to copy
prompts/cleanse.txt                 the exact instruction the cleanse model gets
references/signs-of-ai-writing.md   the full catalogue: 2 vocab tiers, 8 shapes, cadence, rhythm, proof
references/principles.md            the five rewrite principles, each with a real pair
references/sources.md               every source this stands on
examples/ridgeline-roofing.md       full site build, every line before → after
examples/jasper-live-run.md         unedited live run: 3/5 → 5/5 on a real page
```

MIT. Same as the humanizers it stands on.
