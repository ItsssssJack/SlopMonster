#!/usr/bin/env python3
"""Generate skills/slopmonster/SKILL.md from the root SKILL.md.

The root file is the one a human reads and the one upstream carries. The plugin
copy is the same text with every repo-relative path rewritten to
${CLAUDE_PLUGIN_ROOT}/..., because an installed plugin runs from the user's
project directory, where `tools/deslop.py` is not a path to anything.

Two files that must say the same thing will drift, so CI regenerates this one
and fails on a diff rather than trusting anybody to remember.

    python3 tools/build_plugin_skill.py            # write the file
    python3 tools/build_plugin_skill.py --check    # exit red if it is stale
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'SKILL.md'
TARGET = ROOT / 'skills' / 'slopmonster' / 'SKILL.md'

# The three directories the skill tells the agent to run things out of. Anchored
# left on a non-path character so a path already rewritten is not rewritten twice
# and so `references/short-messages.md` inside a longer path is left alone.
DIRS = r'(?:tools|references|prompts)'
PATH = re.compile(r'(?<![\w/${}])(' + DIRS + r'/[\w.-]+)')

BANNER = (
    '<!-- Generated from ../../SKILL.md by tools/build_plugin_skill.py.\n'
    '     Edit the root SKILL.md, not this file. CI checks they match. -->\n'
)


def render(text):
    body = PATH.sub(r'${CLAUDE_PLUGIN_ROOT}/\1', text)
    # Frontmatter must stay the first thing in the file, so the banner goes
    # after the closing --- rather than at the top.
    parts = body.split('---\n', 2)
    if len(parts) == 3 and parts[0] == '':
        return f'---\n{parts[1]}---\n{BANNER}{parts[2]}'
    return BANNER + body


def main():
    want = render(SOURCE.read_text(encoding='utf-8'))
    if '--check' in sys.argv:
        have = TARGET.read_text(encoding='utf-8') if TARGET.exists() else ''
        if have != want:
            sys.exit(f'{TARGET.relative_to(ROOT)} is stale — '
                     'run python3 tools/build_plugin_skill.py')
        print(f'{TARGET.relative_to(ROOT)} is in sync with SKILL.md')
        return
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(want, encoding='utf-8')
    print(f'wrote {TARGET.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
