# Sources

The original pattern catalogue drew on the resources below. The current editorial
guidance also reflects problems found in this repository's README: repetitive
metaphors, unexplained technical claims and sentence pairs that added no useful
information.

## Writing-pattern catalogue

[Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
is maintained by WikiProject AI Cleanup. It provides examples for reviewing text.
A matching pattern alone does not establish who wrote a passage.

The following open-source projects informed the original implementation:

| Project | Contribution to this repository |
|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | Pattern categories drawn from the Wikipedia catalogue. |
| [harshaneel/humanize](https://github.com/harshaneel/humanize) | Research references and punctuation patterns. |
| [lguz/humanize-writing-skill](https://github.com/lguz/humanize-writing-skill) | An editing workflow with multiple passes and vocabulary lists. |
| [haidrrrry/humanize-ai-writing](https://github.com/haidrrrry/humanize-ai-writing) | Instructions that can be used as a standalone editing prompt. |

See each project for its own documentation and license. The implemented rules in
[tools/deslop.py](../tools/deslop.py) determine the score. The broader catalogue in
[signs-of-ai-writing.md](signs-of-ai-writing.md) includes checks that require
editorial judgment.

## Editorial guidance

Steve Krug's *Don't Make Me Think* informs the emphasis on making information easy
to understand. The original marketing examples drew on Daniel Priestley's
problem-first pitch order and Alex Hormozi's work on offers and supporting claims.

[principles.md](principles.md) applies that guidance according to the document's
purpose. A README should explain the project early. A sales page may need to
establish a customer problem before describing the offer. Neither approach calls
for invented evidence.

## Second-model review

The cleanse script routes a draft to a different model family using an installed
CLI. It uses that CLI's configured model and does not pin a model version.

This repository does not establish that a second model will produce a better
edit. Compare the output with the draft for changes in meaning and run the checker
again. The workflow makes no claim to prove human authorship or bypass AI detectors.
