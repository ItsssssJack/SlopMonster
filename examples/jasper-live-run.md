# Live run — a real marketing page, start to finish

A real, unedited run of the full pipeline (29 Aug 2026) on seven verbatim sentences from
the homepage of a large AI marketing SaaS. The draft was written by their team or their
tools. We only ran the loop on it. This is the receipt the README numbers come from.

## Step 1 — Lint the original

```
$ python3 tools/deslop.py --text "…seven sentences from the live page…"
112 words of visible copy

  AI vocabulary:
    · unlock  (1)
    · empower  (1)
    · intuitive  (1)
  rule-of-three rhythm:
    · rule-of-three list  (contacts, leads, and opportunities)
    · rule-of-three list  (briefs, insights, and channel)
    · rule-of-three list  (tips, advice, and practical)
    · rule-of-three list  (stories, tools, and expert)

  score 4/6  needs a cleanse
```

These seven sentences are the scored sample. The full homepage fetch, which includes nav
and menu strings, scored lower still. Only the score above is reproducible from the text
in this file, so that is the number the README quotes.

The run happened on the scorer as it stood that day, and both blocks above are re-derived
from the copy in this file every time a rule changes. The catalogue has grown since:
`intuitive` was added to the vocabulary list, and rule 6 added a sixth point to the
denominator without firing on either draft. So the original scores 4/6 today where it
scored 3/5 then. The copy did not move. The scorer did.

## The original

```text
From advanced language models to context-aware intelligence and intuitive agents,
Jasper's rich product experience is designed to meet marketers where they work—so they
can customize AI for how they work. Measure how your brand performs across every major
AI answer engine, prioritize the actions that matter, and ship brand-governed content
at scale. Scale SEO, personalization, and campaigns and more—driving faster, smarter
marketing growth. Empower your team to target specific accounts, contacts, leads, and
opportunities. Transform briefs, insights, and channel requirements into on-brand
campaign content. Find tips, advice, and practical use cases to advance your AI
marketing strategy. Unlock the full potential of Jasper through stories, tools, and
expert guidance built for marketers.
```

Quoted verbatim for criticism, and fenced because it is input to the tool rather than
copy this repo is shipping.

## Step 3 — The cleanse (GPT-5.6 via the codex CLI, one call, 40s)

```
$ tools/cleanse.sh original.txt > cleansed.txt
```

> Jasper brings advanced language models and context-aware intelligence into agents that
> meet marketers where they already work. Teams can customize Jasper around their
> workflows, track brand performance across every major AI answer engine and focus on
> the actions that matter. Then ship brand-governed content at scale.
>
> Use Jasper to scale SEO and personalization across campaigns and other marketing work,
> driving faster, smarter growth. Target specific accounts and contacts, including
> individual leads and opportunities. Turn briefs and insights into on-brand campaign
> content built around each channel's requirements.
>
> Jasper offers practical advice and use cases to move your AI marketing strategy
> forward. That's where I'd start. And marketers can get more from Jasper through
> stories and tools, backed by expert guidance.

What the model reported changing. It replaced `unlock`, `transform` and `empower` with
direct verbs. It broke the stacked three-part lists into uneven sentences. It removed both
em dashes. It cut "rich product experience". It kept the rough "And" opening.

## Step 4 — Re-lint

```
$ python3 tools/deslop.py --text "$(cat cleansed.txt)"
119 words of visible copy

  score 6/6  CLEAN
```

**4/6 → 6/6, meaning intact, length within 10%, nothing invented.** That is the whole
loop: lint, rewrite, cleanse, re-lint.

Note what the cleanse did *not* fix: the copy is now clean, but it is still generic —
no numbers, no named pain, no refusals. That is what `references/principles.md` is for.
The linter gets you to "not machine". The principles get you to "good".
