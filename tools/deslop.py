#!/usr/bin/env python3
"""Hunt AI tells in the visible copy of a built page. Regex, no opinions, exits red.

    python3 deslop.py index.html
    python3 deslop.py index.html --view view-site     # score one tab only
    python3 deslop.py --text "some copy to check"

This reads only what a visitor can SEE: it strips <script>, <style>, and every HTML
tag, so it scores the words on the page rather than the markup around them.

Scoring is out of 5. Below 5 exits non-zero. That is deliberate — "mostly clean"
copy is how a page ends up sounding like every other AI page on the internet.
"""
import re
import sys

# ── the catalogue ────────────────────────────────────────────────────────────
# Grouped by why they are a tell, because the fix differs per group.

VOCAB = [
    # the words models reach for that humans mostly do not
    'delve', 'delves', 'delving', 'leverage', 'leveraging', 'seamless', 'seamlessly',
    'elevate', 'elevating', 'robust', 'unlock', 'unlocking', 'unleash', 'harness',
    'empower', 'empowering', 'streamline', 'streamlined', 'cutting-edge',
    'state-of-the-art', 'game-changer', 'game-changing', 'revolutionize',
    'revolutionise', 'transformative', 'innovative', 'holistic', 'synergy',
    'paradigm', 'bespoke', 'curated', 'crafted', 'meticulously', 'seamless',
    'realm', 'landscape', 'tapestry', 'testament', 'beacon', 'navigate the',
    'in the world of', 'in today\'s', 'ever-evolving', 'fast-paced',
    'look no further', 'dive in', 'let\'s dive', 'deep dive', 'embark',
    'journey', 'unparalleled', 'unlock the power', 'supercharge', 'turbocharge',
    'effortlessly', 'buckle up', 'the secret sauce', 'level up', 'next-level',
]

PHRASES = [
    # constructions, not words — these are the loudest tells
    (r"\bnot just\b[^.!?]{0,60}\bbut\b",           "the 'not just X, but Y' construction"),
    (r"\bit'?s not (only|just)\b[^.!?]{0,60}\bit'?s\b", "the 'it's not just X, it's Y' construction"),
    (r"\bwhether you'?re\b[^.!?]{0,40}\bor\b",     "the 'whether you're X or Y' opener"),
    (r"\bmore than just\b",                        "'more than just'"),
    (r"\bthat'?s where\b[^.!?]{0,30}\bcomes? in\b", "'that's where X comes in'"),
    (r"\bsay goodbye to\b",                        "'say goodbye to'"),
    (r"\bimagine (a|an|the)\b",                    "the 'imagine a…' opener"),
    (r"\bin conclusion\b|\bto sum up\b",           "essay-summary phrasing"),
    (r"\bwhen it comes to\b",                      "'when it comes to' filler"),
    (r"\bat the end of the day\b",                 "'at the end of the day'"),
    (r"\bthe key is\b|\bthe truth is\b",           "throat-clearing opener"),
    (r"\bhelps? you to\b|\bcan help you\b",        "hedged benefit ('helps you to…')"),
    (r"\bmay potentially\b|\bcould potentially\b|\bmight possibly\b", "stacked hedging"),
    (r"\bvery unique\b|\bquite literally\b",       "intensifier padding"),
]

# invented social proof — the one that gets a real site in trouble
PROOF = re.compile(
    r"([\d][\d,\.]{2,})\s*\+?\s*"
    r"(happy\s+|early\s+|active\s+|satisfied\s+)?"
    r"(users?|customers?|learners?|students?|teams?|members?|companies|businesses)",
    re.I)


def visible_text(html):
    """What a visitor actually reads. Script/style stripped, tags removed."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = (t.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&mdash;', '—')
          .replace('&rarr;', '→').replace('&middot;', '·').replace('&#8209;', '-'))
    return re.sub(r'\s+', ' ', t).strip()


def audit(text):
    hits = {'vocab': [], 'phrases': [], 'punctuation': [], 'rhythm': [], 'proof': []}
    low = text.lower()

    for w in VOCAB:
        n = len(re.findall(rf"(?<!\w){re.escape(w)}(?!\w)", low))
        if n:
            hits['vocab'].append((w, n))

    for pat, label in PHRASES:
        found = re.findall(pat, low)
        if found:
            hits['phrases'].append((label, len(found)))

    # Em-dash density: two or more in one sentence reads as machine cadence.
    # Bounded to a 220-char window on purpose — UI strings (nav items, quiz options,
    # labels) carry no terminal punctuation, so a naive sentence split merges the
    # whole page into one "sentence" and this rule fires on every page. Ask me how
    # I know. A linter that cries wolf gets switched off.
    for s in re.split(r'(?<=[.!?])\s+', text):
        for i in range(0, max(1, len(s)), 220):
            window = s[i:i + 220]
            if window.count('—') >= 2:
                hits['punctuation'].append(('two or more em-dashes in one sentence',
                                            window[:70].strip()))
                break
    if text.count(';') > max(1, len(text) // 2500):
        hits['punctuation'].append(('semicolon-heavy for web copy', f"{text.count(';')} found"))

    # tricolon: "faster, smarter, and better" — the rule-of-three reflex
    for m in re.finditer(r'\b(\w+),\s+(\w+),\s+and\s+(\w+)\b', text):
        a, b, c = m.groups()
        if all(len(x) > 3 for x in (a, b, c)):
            hits['rhythm'].append(('rule-of-three list', m.group(0)[:60]))

    for m in PROOF.finditer(text):
        hits['proof'].append(m.group(0).strip())

    return hits


def report(hits, label=''):
    weights = {'vocab': 1, 'phrases': 1, 'punctuation': 1, 'rhythm': 1, 'proof': 1}
    failed = [k for k, v in hits.items() if v]
    score = 5 - sum(weights[k] for k in failed)
    score = max(0, score)

    titles = {
        'vocab': 'AI vocabulary',
        'phrases': 'AI constructions',
        'punctuation': 'punctuation cadence',
        'rhythm': 'rule-of-three rhythm',
        'proof': 'possible invented proof',
    }

    if label:
        print(f'── {label}')
    for k in ('proof', 'phrases', 'vocab', 'punctuation', 'rhythm'):
        if not hits[k]:
            continue
        print(f'  {titles[k]}:')
        for item in hits[k][:8]:
            print(f'    · {item[0] if isinstance(item, tuple) else item}'
                  + (f'  ({item[1]})' if isinstance(item, tuple) and len(item) > 1 else ''))
        if len(hits[k]) > 8:
            print(f'    · …and {len(hits[k]) - 8} more')

    print(f'\n  score {score}/5', end='  ')
    print('CLEAN' if score == 5 else 'needs a cleanse')
    return score


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    if args[0] == '--text':
        text = ' '.join(args[1:])
    else:
        html = open(args[0]).read()
        if '--view' in args:
            # score one element only: slice from its id= to the next id="view-…"
            vid = args[args.index('--view') + 1]
            start = html.find(f'id="{vid}"')
            if start < 0:
                sys.exit(f'no element with id "{vid}"')
            nxt = html.find('id="view-', start + 1)
            html = html[start:nxt if nxt > 0 else len(html)]
        text = visible_text(html)

    print(f'{len(text.split())} words of visible copy\n')
    sys.exit(0 if report(audit(text)) == 5 else 1)
