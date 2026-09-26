# Signs of AI writing — the catalogue

This catalogue lists patterns to review while editing. It draws on Wikipedia's
*Signs of AI writing*, maintained by WikiProject AI Cleanup, and the projects in
[sources.md](sources.md). These patterns can also appear in human writing.

The five groups correspond to the checker's scoring categories, but some advice
requires editorial judgment and has no regex check. Read the findings in context.
The complete automated rules are in `tools/deslop.py`.

---

## 1 · Vocabulary

Review these words for vague or promotional use. Keep necessary technical terms
and literal meanings when they fit the document, and report any remaining match.

**Words and phrases to review:**
`delve` · `tapestry` · `testament to` · `underscores` · `seamless(ly)` · `robust` ·
`navigate the landscape` · `in today's fast-paced world` · `it's important to note` ·
`it's worth noting` · `that being said` · `at the end of the day` · `unlock` ·
`supercharge` · `elevate` · `game-changing` · `revolutionise` · `harness the power of` ·
`dive deep` · `myriad` · `plethora` · `realm` · `ever-evolving` · `cutting-edge` ·
`transformative` · `paradigm shift` · `synergy` · `holistic` · `embark`

**Additional words to review in context:**
`leverage` · `foster` · `crucial` · `pivotal` · `streamline` · `empower` · `showcase` ·
`curated` · `meticulous` · `compelling` · `innovative` · `comprehensive` · `journey` ·
`solution` · `effortless` · `intuitive` · `world-class` · `best-in-class` · `unleash` · `boost`

The checker does not apply frequency allowances to these editorial lists. Its
implemented vocabulary patterns flag even a single match. Replace vague wording
with an explanation of what happens. Often a plain word such as `use` is enough.

## 2 · Constructions (the shapes)

Review sentence structures as well as individual words:

| Shape | Example | Fix |
|---|---|---|
| `not just X, but Y` | `It's not just a course, it's a journey` | Cut the first clause, keep the claim |
| `more than just` | `More than just another app` | Same |
| `whether you're X or Y` | `Whether you're a beginner or a pro…` | Name the one reader you mean |
| `that's where X comes in` | `That's where Acme comes in` | State what X does |
| `say goodbye to` | `Say goodbye to guesswork` | Name what replaces it |
| `imagine a…` | `Imagine a world where…` | Show it instead |
| hedged benefit | `helps you to`, `can help you` | Describe the benefit at the certainty the evidence supports |
| stacked hedging | `may potentially`, `could possibly` | Remove redundant hedges while preserving uncertainty |
| self-answering question | `The result? Faster shipping.` | A sentence |

Also review adjacent sentences that repeat a metaphor, manufacture a contrast
between audiences or introduce a second hook before explaining the first.
These broader problems require reading the paragraph in context.

Remove unnecessary process commentary and repeated summaries. Use formatting to
help the reader scan. Let paragraph and sentence length follow the material.

## 3 · Punctuation cadence

- Repeated em dashes within a sentence. Check whether the interruptions make it
  harder to follow. The checker uses 220-character windows.
- Stacked hyphenated compounds. The checker flags four within one sentence window.
- Semicolon density. The checker uses a threshold that scales with text length.

Punctuation can be appropriate even when it triggers a pattern. Review readability
and retain qualifications needed for accuracy.

## 4 · Rhythm

The checker recognizes two three-item list patterns, including
`faster, smarter, and better`. Review whether each item contributes information.
Keep a useful list at its natural length. A list's item count cannot establish
who wrote it.

## 5 · Invented proof

Never invent customer counts or other evidence. The checker flags numbers near
certain nouns, but it cannot determine whether the claim is supported. Verify the
claim before using `--allow-proof`, which keeps the warning and removes its score
penalty. Check dates and specifications too, even when no rule flags them.

---

## Review the complete draft

Use [principles.md](principles.md) to check the audience and purpose, the opening,
the progression between sentences, the evidence and the author's voice. Removing
recognized patterns is only part of the edit. Do not force fragments or opinions
into the draft to make it seem personal.
