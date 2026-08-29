#!/usr/bin/env python3
"""Regression tests for the linter. Run: python3 tools/test_deslop.py

Two directions, and the second is the one that matters. It is easy to widen a
regex until it catches everything, so every widening here is paired with a
must-stay-clean case that would break if the rule got greedy.
"""
import re
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deslop import VOCAB, VOCAB_EXACT, audit, visible_text, _root_pattern

fails = []


def check(name, cond, detail=''):
    if not cond:
        fails.append(f'{name}: {detail}')


def groups(text):
    return {k for k, v in audit(text).items() if v}


# ── every catalogue word still fires in its own base form ───────────────────
# The obvious stemming fix (strip a trailing "e") silently kills `elevate`,
# `leverage`, `delve` and ten others. This test is what catches that.
for w in VOCAB:
    check(f'base form "{w}"', re.search(_root_pattern(w), w.lower()),
          'root pattern no longer matches its own base word')
for w in VOCAB_EXACT:
    check(f'exact form "{w}"', 'vocab' in groups(f'We {w} things.'), 'not detected')

# ── inflections fire too: the gap that made the tool half-blind ─────────────
for w in ('elevates', 'unlocks', 'empowers', 'streamlines', 'leverages',
          'harnessing', 'revolutionizes', 'innovation', 'transformational'):
    check(f'inflection "{w}"', 'vocab' in groups(f'Acme {w} your workflow.'), 'missed')

# ── literal senses must NOT fire ────────────────────────────────────────────
# Stemming `crafted` to `craft` would flag a furniture maker. These are the
# words that earn their place on the exact-match list.
for ok in ('We craft furniture by hand in Leeds.',
           'Harness the horse before you load the cart.',
           'They walked the length of the valley.'):
    check('literal sense clean', 'vocab' not in groups(ok), ok)

# ── constructions, contracted and not ───────────────────────────────────────
for bad in ("It's not just a tool, it's a platform.",
            'It is not just a tool, it is a platform.',
            'Whether you are a beginner or a pro, start here.',
            'This is where Acme comes in.',
            "Here's the thing. You need a plan.",
            'The result? Teams ship faster.',
            'Ready to get started?'):
    check('construction caught', 'phrases' in groups(bad), bad)

check('plain "whether you are" is clean',
      'phrases' not in groups('Check whether you are on the latest version.'))

# ── rhythm: the repo's own canonical bad example must fail ──────────────────
check('no-Oxford tricolon', 'rhythm' in groups('Trusted, reliable and built to last.'),
      'the tell quoted in examples/ridgeline-roofing.md scored clean')
check('Oxford tricolon', 'rhythm' in groups('It is faster, smarter, and better.'))
check('short items are not a tricolon', 'rhythm' not in groups('We shipped red, white, and blue.'))
check('fronted adverbial is not a tricolon',
      'rhythm' not in groups('On Tuesday, we shipped the release and went home.'))
# The discriminator that earns the no-Oxford rule its place: a rhetorical
# flourish ends in a phrase, a plain list of services does not. This is the
# repo's own shipped hero line — flagging it would be crying wolf.
check('service list is not a tricolon',
      'rhythm' not in groups('Inspection, repair and replacement for homes and commercial buildings.'))
check('or-list is not a tricolon',
      'rhythm' not in groups('We do not do gutters, siding, windows or conservatories.'))

# ── proof: the canonical fabricated line must fail ──────────────────────────
check('canonical invented proof', 'proof' in groups('Loved by 10,000+ happy homeowners.'),
      'the line quoted in references/principles.md scored clean')
check('small counts too', 'proof' in groups('Trusted by 25 businesses.'))

# ── entities: decoded, not leaked ───────────────────────────────────────────
t = visible_text("<p>It&#x27;s not just a tool, it&#x27;s a platform.</p>")
check('entity apostrophes decoded', "it's not just" in t.lower(), repr(t))
check('entities do not donate semicolons', t.count(';') == 0, repr(t))
check('phrase seen through entities', 'phrases' in groups(t))
check('nbsp becomes a space', visible_text('<p>a&nbsp;b</p>') == 'a b')

# ── the gate: empty input must fail, not pass ───────────────────────────────
here = os.path.dirname(os.path.abspath(__file__))
r = subprocess.run([sys.executable, f'{here}/deslop.py', '--text', ''],
                   capture_output=True, text=True)
check('empty input exits non-zero', r.returncode != 0, f'exit {r.returncode}')
r = subprocess.run([sys.executable, f'{here}/deslop.py', '/nope/missing.html'],
                   capture_output=True, text=True)
check('missing file exits non-zero', r.returncode != 0, f'exit {r.returncode}')
check('missing file has no traceback', 'Traceback' not in r.stderr, r.stderr[:80])

# ── clean human copy still scores 5/5 ───────────────────────────────────────
for ok in ('Six nails per shingle, every shingle.',
           'You get a written scope and a fixed number before anyone climbs a ladder.',
           'We do not do overlays. If the roof needs replacing, it gets stripped.'):
    check('clean copy stays clean', not groups(ok), f'{ok} -> {groups(ok)}')

if fails:
    print(f'{len(fails)} FAILED\n')
    for f in fails:
        print(f'  · {f}')
    sys.exit(1)
print('all tests passed')
