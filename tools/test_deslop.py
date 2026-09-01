#!/usr/bin/env python3
"""Regression tests for the linter. Run: python3 tools/test_deslop.py

Two directions, and the second is the one that matters. It is easy to widen a
regex until it catches everything, so every widening here is paired with a
must-stay-clean case that would break if the rule got greedy.
"""
import re
import subprocess
import sys
import tempfile
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deslop import (VOCAB, VOCAB_EXACT, audit, visible_text, _root_pattern,
                    markdown_prose, PROOF)

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

# ── files are read as UTF-8, whatever the locale ───────────────────────────
# open() with no encoding= uses the locale's, cp1252 on a stock Windows box. A
# UTF-8 page then decodes to mojibake and the em-dash and construction rules
# never fire, so a page full of tells scores CLEAN. Driven through the CLI on
# purpose: --text was always fine, the file paths were the blind spot. Both of
# them: .html goes through visible_text, .md through markdown_prose.
_dir = tempfile.mkdtemp()
_tells = ('It\u2019s not just a tool, it\u2019s a platform. Whether you\u2019re a startup '
          'or an agency, we ship fast \u2014 really fast \u2014 every week.')

for name, body in (('utf8.html', f'<html><body><p>{_tells}</p></body></html>'),
                   ('utf8.md', _tells)):
    path = os.path.join(_dir, name)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(body)
    r = subprocess.run([sys.executable, f'{here}/deslop.py', path],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    check(f'{name} is not decoded as cp1252', r.returncode != 0,
          'a UTF-8 page full of tells scored CLEAN - locale decoding is back')
    check(f'{name}: construction rule fires', 'construction' in r.stdout, r.stdout[:140])
    check(f'{name}: em-dash rule fires', 'em-dash' in r.stdout, r.stdout[:140])

# A flagged snippet outside the console codepage must score, not traceback.
_cjk = os.path.join(_dir, 'cjk.html')
with open(_cjk, 'w', encoding='utf-8') as fh:
    fh.write('<html><body><p>Our seamless platform \u4f60\u597d \u2014 \u4e16\u754c '
             '\u2014 delivers robust value today.</p></body></html>')
r = subprocess.run([sys.executable, f'{here}/deslop.py', _cjk],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
check('non-cp1252 snippet does not traceback', 'Traceback' not in r.stderr, r.stderr[-160:])
check('non-cp1252 snippet still scores', 'score' in r.stdout, r.stdout[:140])

# ── clean human copy still scores 5/5 ───────────────────────────────────────
for ok in ('Six nails per shingle, every shingle.',
           'You get a written scope and a fixed number before anyone climbs a ladder.',
           'We do not do overlays. If the roof needs replacing, it gets stripped.'):
    check('clean copy stays clean', not groups(ok), f'{ok} -> {groups(ok)}')

# ── markdown: a literal is not copy ─────────────────────────────────────────
# Every strip below is paired with a case that must survive it, because the
# fastest way to make a catalogue score 5/5 is to stop reading the catalogue.
md = markdown_prose('Use `delve` here. See [the guide](u.md) for more.')
check('inline code is not scored', 'delve' not in md, repr(md))
check('link text survives', 'the guide' in md, repr(md))
check('surrounding prose survives', 'for more' in md, repr(md))

md = markdown_prose('> ~~Trusted, reliable and built to last.~~\n> **Six nails per shingle.**')
check('struck specimen is not scored', 'rhythm' not in groups(md), repr(md))
check('the shipped line survives', 'Six nails per shingle' in md, repr(md))

md = markdown_prose('Intro.\n```\nleverage seamless unlock\n```\nOutro.')
check('fenced block is not scored', not groups(md), repr(md))
check('prose around the fence survives', 'Intro' in md and 'Outro' in md, repr(md))

# Deleting a code span outright welds the clause into a false rule-of-three.
md = markdown_prose('If a claim needs a number you do not have, write `[needs number]` and move on.')
check('stripping code invents no tricolon', 'rhythm' not in groups(md), repr(md))

# Two table rows are two lines of copy, not one sentence with a dash pile-up.
md = markdown_prose('| a | **3/5** — one thing |\n| b | **5/5** — another thing |')
check('table rows do not merge into one cadence', 'punctuation' not in groups(md), repr(md))

# A heading must not run into the sentence beneath it.
md = markdown_prose('## Receipts, not claims\nA real run on seven sentences.')
check('heading does not weld to body', 'Receipts, not claims A real' not in md, repr(md))

# Markdown handling strips markup only. Real slop in real prose still fails.
md = markdown_prose('We leverage seamless, robust and cutting-edge tooling to empower teams.')
check('markdown does not soften vocabulary', 'vocab' in groups(md), repr(md))
md = markdown_prose('It is not just a tool, it is a journey.')
check('markdown does not soften constructions', 'phrases' in groups(md), repr(md))

md = markdown_prose('- Tier 1 — delete on sight\n- Tier 2 — usually cut')
check('bullets do not merge into one cadence', 'punctuation' not in groups(md), repr(md))
# but a genuine pile-up inside one bullet must still fire
md = markdown_prose('- Our team — trained, certified and local — is ready to help.')
check('dash pile-up inside a bullet still fires', 'punctuation' in groups(md), repr(md))

# ── hyphens: stacking, not the hyphen itself ────────────────────────────────
stack = 'Our industry-leading, context-aware, best-in-class, AI-powered platform ships.'
check('four stacked compounds fire', 'punctuation' in groups(stack), stack)
for ok in ('We fitted a 25-year warranty and a 4.2-hour call-out on a two-storey roof.',
           'The built-up roof needs a full-width strip before the tear-off.',
           'A well-known, long-standing trade name.'):
    check('ordinary hyphenated copy stays clean',
          'punctuation' not in groups(ok), f'{ok} -> {groups(ok)}')

md = markdown_prose('> ~~Em-dash pile-up~~\n> **Thirty-eight on the crew, factory-trained today.**')
check('blockquote lines do not merge', 'punctuation' not in groups(md), repr(md))

# ── proof: a number and its noun live in one sentence ───────────────────────
for hit in ('10,000+ happy users', '500 teams', '2,000 verified customers',
            '3.5 million customers'):
    check('real proof claim still caught', PROOF.search(hit), hit)
for clean in ('"Don\'t Make Me Think", 2000. The reader decides in seconds.',
              'Roofing, and only roofing, since 2001. Customers come back.',
              'Version 2.0. Readers can skip it.'):
    check('proof does not reach across a full stop', not PROOF.search(clean), clean)

if fails:
    print(f'{len(fails)} FAILED\n')
    for f in fails:
        print(f'  · {f}')
    sys.exit(1)
print('all tests passed')
