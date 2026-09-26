---
name: slopmonster
description: Review writing for its intended reader, check common AI writing patterns, revise, request a second pass from a different model family, and check again. Trigger on /slopmonster, "humanize this", "de-slop this", "does this sound like AI", "fix this copy".
---

# SlopMonster

Edit the supplied draft for its audience and purpose. The workflow supports
READMEs, landing pages, emails and scripts. Use the checker to locate known
patterns, then review the writing in context. A score of 5/5 means no scored
patterns matched; it does not establish that the copy is clear or accurate.

## Step 1: Establish the context and run the checker

Identify the reader, the format and what the reader needs from the text. Use the
user's brief and the draft itself. Ask a focused question only when missing context
would materially change the edit.

A README should explain what the project does, how to use it and its limitations.
A sales page may need an opening that establishes a problem. An email may need to
start with the request. Choose an approach that fits the document.

```bash
python3 tools/deslop.py draft.md
python3 tools/deslop.py page.html
python3 tools/deslop.py page.html --view view-site
python3 tools/deslop.py --text "paste a draft"
```

The checker scores five categories: vocabulary, sentence patterns, punctuation,
three-item lists and possible unsupported proof. Each category with a match costs
one point. Below 5/5 it exits with status 1. Empty input also fails.

For Markdown, use the file path so code and quoted specimens are handled as
Markdown. The rules are English only and do not detect the input language.

## Step 2: Review and rewrite

Read [references/principles.md](references/principles.md) for the editorial checks
and [references/signs-of-ai-writing.md](references/signs-of-ai-writing.md) for the
pattern catalogue.

Work through the draft in this order:

1. **Purpose and structure.** Answer the reader's first question early. Remove
   duplicate hooks and curiosity gaps that delay an explanation. Keep each
   paragraph focused on a useful point, with enough context to understand it.
2. **Meaning and evidence.** Check that each sentence adds information and follows
   from what came before. Explain conditions on claims. Remove empty contrasts,
   repeated metaphors and comparisons that do not help the reader. Preserve
   facts, technical behavior and the author's position.
3. **Wording and rhythm.** Review the checker findings and replace vague language
   with direct wording. Read adjacent sentences together for repetitive shapes.
   Let sentence length follow the thought. Keep useful lists and punctuation.

Do not manufacture personality by adding an opinion, a mistake, a fragment or a
fixed quota of short sentences. Do not add a number to every claim. Use only facts
supplied by the author or verified from an appropriate source.

The checker can flag valid language. Review the actual match before editing it.
Never hide ordinary prose in code formatting to raise the score. If a necessary
phrase still triggers a rule, explain the remaining finding to the user.

## Step 3: Request a second editing pass

Use a different model family from the one that wrote the draft. This provides a
second review with the same audience and purpose; inspect its suggestions before
accepting them.

| Draft written with | Command |
|---|---|
| Claude | `DESLOP_WRITER=claude tools/cleanse.sh draft.md > cleansed.md` |
| GPT / Codex / ChatGPT | `DESLOP_WRITER=gpt tools/cleanse.sh draft.md > cleansed.md` |
| Gemini | Use either command to select an installed rival CLI. |

The script uses the selected CLI's configured model and
[prompts/cleanse.txt](prompts/cleanse.txt). The CLI must be installed and
authenticated. If it is unavailable, use the prompt and draft in the other model
family's chat. If a second model cannot be accessed, report that the pass was not
completed and continue the editorial review and local checks.

Standard output contains the edited copy. Standard error contains change notes.
To keep both:

```bash
DESLOP_WRITER=gpt tools/cleanse.sh draft.md > cleansed.md 2> notes.txt
```

Check the command's exit status. A timeout returns 124. A missing rival CLI returns
127 and prints the prompt and input as standard output; that output is not an
edited draft. Other CLI failures also need to be resolved before using the file.

The model separates its notes with `<<<SLOPMONSTER-NOTES>>>`. A warning about a
missing marker means notes may have been included in the copy. Inspect the result.

## Step 4: Compare the edit and check again

Compare the result with the source. Check facts and commands for changes, confirm
that links and placeholders survived, and read the opening in context. Review the
notes for deletions that may have removed necessary information.

```bash
python3 tools/deslop.py cleansed.md
```

Aim to resolve the checker findings while preserving the intended meaning. Report
any justified exceptions. The final editorial review is required even at 5/5.

If you change a regex, run `python3 tools/test_deslop.py`. If you change the cleanse
script, run `bash tools/test_cleanse.sh`.

## Factual claims

Never invent evidence. This includes customer counts, testimonials, ratings and
results. If the draft needs missing information, flag it for the author with a
placeholder such as `[needs number]`. Do not publish an unresolved placeholder as
a verified claim.

The proof rule only sees number-and-noun patterns. It cannot verify whether a claim
is true. Use `--allow-proof` only after checking the evidence; the option retains
the warning while removing its score penalty.

## Output

Return the rewritten copy or save the edited artifact as requested. Then give up
to five short notes explaining substantive changes and the check results. State
whether the second model pass completed. Keep any unresolved claims or remaining
checker findings visible. Do not claim the edit proves human authorship.
