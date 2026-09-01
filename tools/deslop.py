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
import html as _html   # aliased: `visible_text` takes a parameter named `html`
import re
import sys

# ── the catalogue ────────────────────────────────────────────────────────────
# Grouped by why they are a tell, because the fix differs per group.

# Matched by root, so every inflection fires: `elevate` also catches elevates,
# elevated, elevating, elevation. Landing-page copy is written in the third
# person ("Acme elevates your workflow"), so exact-string matching missed the
# single most common surface form of every word here.
VOCAB = [
    'delve', 'leverage', 'seamless', 'elevate', 'robust', 'unlock', 'unleash',
    'empower', 'streamline', 'cutting-edge', 'state-of-the-art', 'game-changer',
    'game-changing', 'revolutionize', 'revolutionise', 'transformative',
    'transformation', 'innovate', 'holistic', 'synergy', 'synergies', 'paradigm', 'bespoke',
    'meticulous', 'tapestry', 'testament', 'beacon', 'unparalleled', 'supercharge',
    'turbocharge', 'effortless', 'next-level',
    # second tier: fine once in a long page, damning in every section
    'pivotal', 'foster', 'showcase', 'compelling', 'intuitive', 'world-class',
    'best-in-class',
]

# Words with an ordinary literal sense — "we craft furniture", "harness the
# horse", "the landscape of the valley". Matched exactly, never by root, so the
# innocent use survives and only the marketing inflection is caught.
VOCAB_EXACT = [
    'crafted', 'curated', 'harnessing', 'harness the power', 'journey', 'realm', 'landscape',
    'navigate the', 'in the world of', "in today's", 'ever-evolving', 'fast-paced',
    'look no further', 'dive in', "let's dive", 'deep dive', 'embark',
    'unlock the power', 'buckle up', 'the secret sauce', 'level up',
]


def _root_pattern(word):
    """A regex matching `word` and its inflections.

    Strip a trailing e/ed/ing/ly to get the root, then allow the suffixes back.
    The bare `e?` alternative is load-bearing: without it, stripping the `e` from
    `elevate` leaves `elevat`, which no longer matches the base form itself.
    """
    root = re.sub(r'(ed|ing|ly|e)$', '', word)
    if len(root) < 4:                     # too short to stem safely
        return rf"(?<!\w){re.escape(word)}(?!\w)"
    return rf"(?<!\w){re.escape(root)}(?:e|es|ed|ing|ion|ions|ional|ive|al|ally|s|ly|ness)?(?!\w)"

PHRASES = [
    # constructions, not words — these are the loudest tells
    # The contracted and uncontracted forms both matter: formal register is not an
    # adversarial rewrite, it is the default thing a model emits.
    (r"\bnot (just|only|merely|simply)\b[^.!?]{0,80}\bbut\b", "the 'not just X, but Y' construction"),
    (r"\bit(?:'?s| is) not (only|just)\b[^.!?]{0,80}\bit(?:'?s| is)\b", "the 'it's not just X, it's Y' construction"),
    (r"\bwhether you(?:'?re| are)\b[^.!?]{0,40}\bor\b", "the 'whether you're X or Y' opener"),
    (r"\bmore than just\b",                        "'more than just'"),
    (r"\b(that|this)(?:'?s| is) where\b[^.!?]{0,30}\bcomes? in\b", "'that's where X comes in'"),
    (r"\bsay goodbye to\b",                        "'say goodbye to'"),
    (r"\bimagine (a|an|the)\b",                    "the 'imagine a…' opener"),
    (r"\bin conclusion\b|\bto sum up\b",           "essay-summary phrasing"),
    (r"\bwhen it comes to\b",                      "'when it comes to' filler"),
    (r"\bat the end of the day\b",                 "'at the end of the day'"),
    (r"\bthe key is\b|\bthe truth is\b",           "throat-clearing opener"),
    (r"\bhelps? you to\b|\bcan help you\b",        "hedged benefit ('helps you to…')"),
    (r"\bmay potentially\b|\bcould potentially\b|\bmight possibly\b", "stacked hedging"),
    (r"\bvery unique\b|\bquite literally\b",       "intensifier padding"),
    # Openers and self-answering questions. Cheap literals, near-zero false
    # positives, and they cover the register a pure vocabulary list cannot see.
    (r"\bhere'?s the thing\b|\blet'?s break (it|this) down\b|\bthe best part\b",
                                                   "throat-clearing opener"),
    (r"\bready to get started\b|\blet'?s get started\b", "boilerplate CTA"),
    (r"\bthe (result|answer|catch|kicker|upshot)\?\s", "self-answering question"),
]

# Invented social proof. Deliberately broad: this is the one mistake with no
# route back, so recall matters more than precision. If your number is real and
# you can evidence it, pass --allow-proof and the rule drops to advisory.
# Hyphenated compound modifiers. One is ordinary English: "a 25-year warranty".
# Four in a sentence is a model reaching for authority it has not earned, and the
# giveaway is that they stack in front of one noun: "our industry-leading,
# context-aware, best-in-class, AI-powered platform". The floor is high on purpose.
# Real trade copy runs one to three per hundred words, and stacked slop runs sixty.
COMPOUND = re.compile(r'\b[a-z]{2,}-[a-z]{2,}(?:-[a-z]{2,})*\b', re.I)
COMPOUND_FLOOR = 4

PROOF = re.compile(
    # Digits, thousands separators and a decimal point, but never a trailing
    # full stop. Absorbing it let "Don't Make Me Think, 2000. The reader…" read
    # as a proof claim, because the year swallowed the sentence break and then
    # reached across it for a noun. A number and its noun live in one sentence.
    r"([\d][\d,]*(?:\.\d+)?)\s*\+?\s*"
    r"((?:happy|early|active|satisfied|verified|trusted|delighted)\s+)?"
    r"(?:\w+\s+){0,1}"
    r"(users?|customers?|learners?|students?|teams?|members?|companies|businesses"
    r"|homeowners?|subscribers?|clients?|patients?|readers?|sites?|projects?)",
    re.I)


def normalise(t):
    """Fold the typographic variants back to the plain ones the rules match.

    A non-breaking hyphen is not `-`, \xa0 is not a space, and a curly
    apostrophe is not `'`. Miss any of them and `cutting-edge`,
    `it's not just X` and `whether you're` all stop matching on real copy,
    because real copy is exactly where the pretty characters come from.

    Every input path runs through here. Markdown skipped it once, and the
    construction rules went blind on every .md file with a smart quote in it.
    """
    t = t.replace('‑', '-').replace('\xa0', ' ').replace('’', "'")
    return re.sub(r'\s+', ' ', t).strip()


def visible_text(html):
    """What a visitor actually reads. Script/style stripped, tags removed."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    # Decode every entity, not a hand-written six. Numeric entities used to leak
    # through as literal text: each `&#x27;` donated a phantom semicolon to the
    # punctuation rule, and every apostrophe-encoded page went blind to the
    # `it's not just X` and `whether you're` patterns.
    t = _html.unescape(t)
    return normalise(t)


def read_utf8(path):
    """Read a file as UTF-8, whatever the machine's locale says.

    open() with no encoding= uses the locale's, which is cp1252 on a stock
    Windows install. A UTF-8 page then decodes its em-dashes and curly
    apostrophes into mojibake, .replace('\u2019', "'") never fires, and
    window.count('\u2014') counts zero. The punctuation and construction rules
    go silently blind: the same copy scores 4/5 through --text and 5/5 CLEAN
    from a file path, and the file path is what CI wires in.

    A gate that passes because it cannot read is worse than no gate at all.
    Reported by @Azrael259 in #3, who hit it on Windows.
    """
    return open(path, encoding='utf-8', errors='replace').read()


def markdown_prose(md):
    """The prose of a Markdown file, with the specimens removed.

    A literal is not copy. A README that documents `delve` has not shipped the
    word, it has quoted it, and a linter that cannot tell the difference makes
    every catalogue score zero. So four things come out before scoring:

      fenced blocks   ```…```      commands and code, never prose
      inline code     `delve`      the specimen being named
      struck text     ~~before~~   the line being shown as wrong, on purpose
      images          ![alt](src)  alt text is metadata, not body copy

    Link text stays, because that is read as part of the sentence. Everything
    else is scored exactly as before: this strips markup, it does not soften a
    single rule.
    """
    md = re.sub(r'```.*?```', ' ', md, flags=re.S)
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' . ', md)
    md = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', md)
    # Stand-ins, not deletions. Removing `[needs number]` outright welds
    # "you do not have, write ... and move on" into a false rule-of-three, and
    # a linter that invents a hit is worse than one that misses. Two letters
    # keep the clause intact without ever matching a rule itself.
    md = re.sub(r'`[^`]*`', ' it ', md)
    md = re.sub(r'~~.*?~~', ' it ', md, flags=re.S)
    # Headings, table cells and rows are separate copy, not one long sentence.
    # Joined, two em-dashes from two table rows read as one machine cadence.
    md = re.sub(r'^\s{0,3}#{1,6}\s*(.*)$', r' . \1 . ', md, flags=re.M)
    md = re.sub(r'\|', ' . ', md)
    # A bullet is its own line of copy. Left joined, two list items donate one
    # em-dash each and read as a single machine cadence that nobody wrote.
    md = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', ' . ', md, flags=re.M)
    md = re.sub(r'^\s*>\s?', ' . ', md, flags=re.M)
    md = re.sub(r'[*_>]', ' ', md)
    return normalise(md)


def audit(text):
    hits = {'vocab': [], 'phrases': [], 'punctuation': [], 'rhythm': [], 'proof': []}
    low = text.lower()

    for w in VOCAB:
        n = len(re.findall(_root_pattern(w), low))
        if n:
            hits['vocab'].append((w, n))

    for w in VOCAB_EXACT:
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
    for s in re.split(r'(?<=[.!?])\s+', text):
        for i in range(0, max(1, len(s)), 220):
            window = s[i:i + 220]
            found = COMPOUND.findall(window)
            if len(found) >= COMPOUND_FLOOR:
                hits['punctuation'].append((f'{len(found)} hyphenated compounds stacked '
                                            'in one sentence', ', '.join(found[:4])))
                break

    # Floor of 3: two semicolons in a long technical page is a style, not a tell.
    if text.count(';') > max(3, len(text) // 1200):
        hits['punctuation'].append(('semicolon-heavy for web copy', f"{text.count(';')} found"))

    # Tricolon: the rule-of-three reflex. Two shapes, deliberately narrow.
    #
    # With the Oxford comma, three single words: "faster, smarter, and better".
    # Without it, the third item must be a 2–3 word phrase that ends the clause:
    # "Trusted, reliable and built to last". That phrase requirement is what
    # separates a rhetorical flourish from a plain list of services —
    # "Inspection, repair and replacement for homes" is three real things a
    # roofer does, and flagging it would be exactly the wolf-crying that gets a
    # linter switched off.
    for pat in (r'\b(\w{4,}),\s+(\w{4,}),\s+and\s+(\w{4,})\b',
                r'\b(\w{4,}),\s+(\w{4,})\s+and\s+((?:\w+\s+){1,2}\w+)\s*[.!?,;:]'):
        for m in re.finditer(pat, text):
            hits['rhythm'].append(('rule-of-three list', m.group(0)[:60]))

    for m in PROOF.finditer(text):
        hits['proof'].append(m.group(0).strip())

    return hits


def report(hits, label='', allow_proof=False):
    weights = {'vocab': 1, 'phrases': 1, 'punctuation': 1, 'rhythm': 1, 'proof': 1}
    if allow_proof:
        # The one rule a regex cannot judge: it sees a number beside a noun, not
        # whether you can evidence it. --allow-proof still prints the hits, but
        # stops a true, defensible claim from blocking a green build forever.
        weights['proof'] = 0
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
    # Reading UTF-8 correctly means real non-ASCII now reaches print(), and a
    # Windows console is cp1252: one CJK character or emoji inside a flagged
    # snippet would end the run in a UnicodeEncodeError traceback. Replace
    # rather than raise. Naming the tell is the job; echoing it byte-for-byte
    # is not, and the suite already asserts this tool never shows a traceback.
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):      # already-wrapped or exotic stream
        pass

    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)

    allow_proof = '--allow-proof' in args
    args = [a for a in args if a != '--allow-proof']

    as_md = '--markdown' in args
    args = [a for a in args if a != '--markdown']

    if args[0] == '--text':
        text = ' '.join(args[1:])
        if as_md:
            text = markdown_prose(text)
    elif args[0].endswith('.md') or as_md:
        try:
            text = markdown_prose(read_utf8(args[0]))
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            sys.exit(f'deslop: cannot read {args[0]}: {e.strerror}')
    else:
        try:
            html = read_utf8(args[0])
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            sys.exit(f'deslop: cannot read {args[0]}: {e.strerror}')
        if '--view' in args:
            # score one element only: slice from its id= to the next id="view-…"
            vid = args[args.index('--view') + 1]
            start = html.find(f'id="{vid}"')
            if start < 0:
                sys.exit(f'no element with id "{vid}"')
            nxt = html.find('id="view-', start + 1)
            html = html[start:nxt if nxt > 0 else len(html)]
        text = visible_text(html)

    # Nothing to score is a failure, not a pass. A cleanse that times out leaves a
    # zero-byte file, and a gate that stamps an empty file CLEAN reports slop as
    # clean at exactly the moment the pipeline broke.
    if not text.split():
        sys.exit('deslop: no visible copy to score — empty input')

    print(f'{len(text.split())} words of visible copy\n')
    sys.exit(0 if report(audit(text), allow_proof=allow_proof) == 5 else 1)
