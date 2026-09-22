#!/usr/bin/env python3
"""Hunt AI tells in the visible copy of a built page. Regex, no opinions, exits red.

    python3 deslop.py index.html
    python3 deslop.py index.html --view view-site     # score one tab only
    python3 deslop.py --text "some copy to check"

This reads only what a visitor can SEE: it strips <script>, <style>, and every HTML
tag, so it scores the words on the page rather than the markup around them.

Scoring is out of 6. Below 6 exits non-zero. That is deliberate — "mostly clean"
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

# Negated "just/only/merely/simply", in either register.
#
# `\bnot\b` cannot match inside `isn't` — there is no standalone `not` token there — so
# an uncontracted-only pattern misses every contracted form, which is the register a
# model reaches for when it is trying hardest to sound human. Matching the `n't` suffix
# covers isn't / aren't / wasn't / doesn't / don't / won't / can't without enumerating
# them. Straight and curly apostrophes both.
_NEG_JUST = r"(?:\bnot|n['’]t)\s+(?:just|only|merely|simply)\b"

# The Y clause of the swap, reached across a comma or a single full stop. It is not
# always a copula — "it doesn't just park you, it GETS you there" is the same move — so
# this takes a pronoun subject and lets any verb follow. The punctuation carries the
# precision: "It's not just about money." has no Y clause and stays clean, and so does
# "Do not just take my word for it."
_XY_TAIL = r"[^!?]{0,80}?[,.]\s*(?:it|this|that|they|we|you|he|she|i)\b"

PHRASES = [
    # constructions, not words — these are the loudest tells
    # The contracted and uncontracted forms both matter: formal register is not an
    # adversarial rewrite, it is the default thing a model emits.
    (_NEG_JUST + r"[^.!?]{0,80}\bbut\b", "the 'not just X, but Y' construction"),
    (_NEG_JUST + _XY_TAIL, "the 'not just X, it's Y' construction"),
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
    r"|homeowners?|subscribers?|clients?|patients?|readers?|sites?|projects?)"
    # Closed with a word boundary, like `_root_pattern`. Without it `sites?`
    # matched inside "sitemaps", `teams?` inside "teamsters" and `projects?`
    # inside "projectors", and "12 sitemaps" scored as invented social proof.
    r"(?!\w)",
    re.I)


def _sentences(text):
    """Split on terminal punctuation. Every rule that judges a sentence uses this."""
    return re.split(r'(?<=[.!?])\s+', text)


def _windows(s, size=220):
    """A sentence in fixed slices.

    UI strings — nav items, quiz options, labels — carry no terminal
    punctuation, so a naive split merges a whole page into one "sentence" and
    any density rule then fires on every page. Slicing caps the damage.
    """
    for i in range(0, max(1, len(s)), size):
        yield s[i:i + size]


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


# ── rule 6: aphoristic clause-pairing ────────────────────────────────────────
# Rules 1-5 all hunt something lexical: a banned word, a fixed template, a
# punctuation count. Much of what makes AI prose read as AI is none of those.
# It is a rhythm. Two short clauses stitched together with no logical connector,
# where the second echoes, relabels or one-ups the first. This README scored a
# clean 5/5 while doing it in four separate paragraphs. See issue #10.
#
# Three shapes score. Two more print and deliberately do not move the score:
# they are the loose end of the same family, and measured against ordinary
# business English they fire often enough that a hard gate built on them would
# cry wolf. The advisory block is a reading aid, not a verdict.

MAX_SCORE = 6

# A space-padded full stop is markdown structure, not a sentence ending. A real
# terminator is glued to its word ("ship."); `markdown_prose` writes " . " for a
# heading, a bullet, a blockquote marker and a table cell. So two bullets never
# read as an adjacent pair, and a heading never pairs with the body under it.
# HTML never produces the shape, so this costs the `visible_text` path nothing.
BARRIER = re.compile(r'(?:^|\s)\.(?:\s|$)')

# The sentence split breaks after "e.g." and "No." too. Rules 3 and 4 never
# cared, because they judge one sentence. Rule 6 reaches across the break.
ABBREV = frozenset('e.g. i.e. etc. vs. cf. no. fig. ch. pp. mr. mrs. dr. st.'.split())

_WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")

# Function words, too common to mean anything when two clauses share one.
PAIRING_STOP = frozenset("""
about above after again against almost along already also although always among another
because become becomes been before behind being below beside besides better between beyond
both bring cannot come could does doing done down during each either enough even ever
every everything except first from further getting given gives going gone have having
here hers himself his however inside instead into itself just keep kept like made make
makes making many maybe might more most much must myself near needs neither never next
nobody none nothing often once only other others ought ourselves outside over past
perhaps please quite rather really same seems several shall should simply since some
something sometimes soon still such taken takes than that their theirs them themselves
then there these they thing things this those though through thus together toward under
until upon used uses using very want well went were what when where whether which while
whole whose will with within without would your yours yourself
""".split())

# "Developers call this a linter. Everyone else can call it a checker that will
# not let you ship." Two adjacent sentences that each relabel the same thing for
# a different audience. The object must be third person, which is what keeps
# every "call us today" out of it.
CALL = re.compile(
    r"^(.*?)\b(?:can|could|would|will|may|might)?\s*calls?\s+"
    r"(?:it|this|that|these|those|them)\s+"
    r"(?:a|an|the)?\s*([a-z][a-z-]{2,})", re.I)

# The guard that keeps the function-invocation sense out: "The client calls it
# once at startup. The server calls it again on reconnect." is not a relabel.
CALL_ADVERB = frozenset("""
once twice again back later directly first last home out off now then early often
daily nightly twice repeatedly asynchronously synchronously internally externally
""".split())

_ORDINALS = 'first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth'

# "Four groups strip the AI accent. The fifth asks whether the line sells
# anything." A count opens one sentence and an ordinal opens the next. Counting
# used as rhythm rather than as information.
COUNT_OPEN = re.compile(r'^\s*(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+[a-z]',
                        re.I)
ORDINAL_OPEN = re.compile(rf'^\s*the\s+({_ORDINALS})\s+([\w-]+)', re.I)

# The whole precision of the rule sits here: the ordinal must be pronominal,
# with its noun elided. Slop writes "The fifth asks whether…". Ordinary prose
# writes "The fifth test is the slow one", and that must stay clean.
ORDINAL_NOUN = frozenset("""
thing things item items group groups step steps rule rules section sections test tests
case cases option options example examples chapter chapters pass passes line lines file
files field fields column columns row rows point points note notes version versions word
words source sources tool tools model models team teams user users one ones people
person sentence sentences paragraph paragraphs release releases commit commits
""".split())
ORDINAL_VERB = frozenset("""
is was are were does do did has have had goes comes came asks adds matters counts sells
tells makes takes gets says can cannot will must should would could might shows means
answers explains checks catches runs reads writes holds stops starts ends belongs
""".split())

# "a page that smells of it is a page they stop trusting." The same head noun
# opens and closes the clause, so the sentence arrives back where it started
# instead of developing.
#
# Both determiners must be INDEFINITE, and that restriction is the rule. The
# definite form is a referential identity claim carrying real information —
# "The default branch in that repo is the branch the workflow checks out",
# "The first argument you pass is the argument the callback receives". Five of
# five ordinary technical sentences of that shape fire on the naive version.
# A linter that cries wolf gets switched off.
#
# The two-modifier tolerance is what sees "a sales failure before it is a
# writing failure", and it is only safe because of the indefinite restriction.
# The two decisions are coupled. Do not keep one without the other.
#
# "A backup that is not restored is not a backup" stays clean for free: the
# determiner must follow the copula immediately, and negation puts `not` there.
CHIASMUS = re.compile(
    r'\b(?:a|an)\s+(?:[a-z]+\s+){0,2}?([a-z]{4,})\b'
    r'[^.!?]{2,60}?'
    r'\b(?:is|was|are|were)\s+(?:a|an)\s+(?:[a-z]+\s+){0,2}?\1\b'
    r'[^.!?]{0,60}', re.I)

# A subordinator IS the logical connector whose absence defines a flat splice.
SPLICE_SUBORDINATOR = re.compile(
    r'\b(?:because|since|so|then|therefore|thus|which|when|while|if|unless|after|'
    r'before|although|though|whereas|until|once)\b', re.I)
SPLICE_SUBJECT = re.compile(r"^(?:a|an|the|it|this|that|they|we|you|i|he|she|there)\b|^[A-Z]")

ADVISORY_CAP = 5


def _words(s):
    return _WORD.findall(s)


def _content(s):
    """The words in a clause that could carry an echo. Everything else is glue."""
    return {w.lower() for w in _words(s)
            if len(w) >= 5 and w.lower() not in PAIRING_STOP}


def _units(text):
    """Sentences that are real copy, with markdown structure removed entirely.

    A segment touching a space-padded full stop came from a heading, a bullet,
    a table cell or a blockquote marker. It is dropped rather than kept, because
    keeping it would let a list item pair with the sentence printed next to it.
    """
    for s in _sentences(text):
        s = s.strip()
        if not s or BARRIER.search(s) or not _WORD.search(s):
            continue
        yield s


def _pairs(units):
    """Adjacent sentences, minus the ones the split got wrong.

    A first member ending in an abbreviation is not a finished sentence, so the
    thing after it is not the next sentence.
    """
    for a, b in zip(units, units[1:]):
        tail = a.split()[-1].lower() if a.split() else ''
        if tail in ABBREV or (len(tail) <= 3 and tail.endswith('.')):
            continue
        yield a, b


def _relabel(s):
    """The label a clause hangs on a thing, and who is doing the hanging."""
    if re.match(r'^\s*call\b', s, re.I):
        return None                      # an imperative: "Call the office by nine."
    m = CALL.search(s)
    if not m:
        return None
    subject, label = m.group(1).strip().lower(), m.group(2).lower()
    if label in CALL_ADVERB:
        return None                      # "the client calls it once at startup"
    return subject, label


def _ordinal_drumbeat(a, b):
    if len(_words(a)) > 14 or len(_words(b)) > 16:
        return False
    if not COUNT_OPEN.match(a):
        return False
    m = ORDINAL_OPEN.match(b)
    if not m:
        return False
    nxt = m.group(2).lower()
    if nxt in ORDINAL_NOUN:
        return False                     # "The fourth test is the slow one."
    return nxt in ORDINAL_VERB or (nxt.endswith(('s', 'ed')) and len(nxt) > 3)


def clause_pairing(text):
    """Rule 6. Returns (scored, advisory), each a list of (label, snippet)."""
    scored, advisory = [], []
    units = list(_units(text))
    pairs = list(_pairs(units))

    for a, b in pairs:
        ra, rb = _relabel(a), _relabel(b)
        if (ra and rb and ra[0] != rb[0] and ra[1] != rb[1]
                and len(_words(a)) <= 14 and len(_words(b)) <= 14):
            scored.append(('relabel-pairing', f'{a[:38]} … {b[:38]}'))
        if _ordinal_drumbeat(a, b):
            scored.append(('ordinal-drumbeat', f'{a[:38]} … {b[:38]}'))

    for s in units:
        m = CHIASMUS.search(s)
        if m:
            scored.append((f'noun-chiasmus on "{m.group(1).lower()}"', m.group(0)[:70].strip()))

    # A word the whole document is about repeats for honest reasons. Damping on
    # document frequency is what takes the advisory block from unreadable to
    # worth reading: `roof`, `scorer`, `model` and `copy` stop counting.
    freq = {}
    for s in units:
        for w in _content(s):
            freq[w] = freq.get(w, 0) + 1

    for a, b in pairs:
        wa, wb = _words(a), _words(b)
        if not (3 <= len(wa) <= 12 and 3 <= len(wb) <= 12):
            continue
        shared = {w for w in _content(a) & _content(b)
                  if freq.get(w, 0) <= 3 and not any(c.isdigit() for c in w)}
        if shared:
            advisory.append((f"echo-pairing on \"{sorted(shared)[0]}\"",
                             f'{a[:33]} … {b[:33]}'))

    for s in units:
        halves = re.split(r',\s+and\s+', s)
        if len(halves) != 2:
            continue
        left, right = halves[0].strip(), halves[1].strip(' .!?')
        if ',' in left or ',' in right:
            continue                     # three items is a tricolon, rule 4's job
        if not (5 <= len(_words(left)) <= 14 and 5 <= len(_words(right)) <= 14):
            continue
        if not SPLICE_SUBJECT.match(right) or SPLICE_SUBORDINATOR.search(right):
            continue
        if _content(left) & _content(right):
            continue                     # that is an echo, already reported above
        advisory.append(('flat-splice', s[:70].strip()))

    return scored, advisory[:ADVISORY_CAP]


def audit(text):
    hits = {'vocab': [], 'phrases': [], 'punctuation': [], 'rhythm': [], 'proof': [],
            'pairing': [], 'echo': []}
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
    for s in _sentences(text):
        for window in _windows(s):
            if window.count('—') >= 2:
                hits['punctuation'].append(('two or more em-dashes in one sentence',
                                            window[:70].strip()))
                break
    for s in _sentences(text):
        for window in _windows(s):
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
    # "Inspection, repair and replacement for homes and commercial buildings"
    # is three real things a roofer does, its third item runs long, and
    # flagging it would be exactly the wolf-crying that gets a linter switched
    # off. Note the shape is what is judged, not the meaning: a three-word
    # closing item ("replacement for homes") does fire, by design.
    for pat in (r'\b(\w{4,}),\s+(\w{4,}),\s+and\s+(\w{4,})\b',
                r'\b(\w{4,}),\s+(\w{4,})\s+and\s+((?:\w+\s+){1,2}\w+)\s*[.!?,;:]'):
        for m in re.finditer(pat, text):
            hits['rhythm'].append(('rule-of-three list', m.group(0)[:60]))

    for m in PROOF.finditer(text):
        hits['proof'].append(m.group(0).strip())

    hits['pairing'], hits['echo'] = clause_pairing(text)

    return hits


def report(hits, label='', allow_proof=False):
    weights = {'vocab': 1, 'phrases': 1, 'punctuation': 1, 'rhythm': 1, 'proof': 1,
               'pairing': 1,
               # Weight 0 is the same mechanism --allow-proof already uses: the
               # hits print, they just never move the score. The two loose
               # clause-pairing shapes live here permanently.
               'echo': 0}
    if allow_proof:
        # The one rule a regex cannot judge: it sees a number beside a noun, not
        # whether you can evidence it. --allow-proof still prints the hits, but
        # stops a true, defensible claim from blocking a green build forever.
        weights['proof'] = 0
    failed = [k for k, v in hits.items() if v]
    score = MAX_SCORE - sum(weights[k] for k in failed)
    score = max(0, score)

    titles = {
        'vocab': 'AI vocabulary',
        'phrases': 'AI constructions',
        'punctuation': 'punctuation cadence',
        'rhythm': 'rule-of-three rhythm',
        'proof': 'possible invented proof',
        'pairing': 'aphoristic clause-pairing',
        'echo': 'clause echo and flat splice (advisory, not scored)',
    }

    if label:
        print(f'── {label}')
    for k in ('proof', 'phrases', 'vocab', 'punctuation', 'rhythm', 'pairing', 'echo'):
        if not hits[k]:
            continue
        print(f'  {titles[k]}:')
        for item in hits[k][:8]:
            print(f'    · {item[0] if isinstance(item, tuple) else item}'
                  + (f'  ({item[1]})' if isinstance(item, tuple) and len(item) > 1 else ''))
        if len(hits[k]) > 8:
            print(f'    · …and {len(hits[k]) - 8} more')

    print(f'\n  score {score}/{MAX_SCORE}', end='  ')
    print('CLEAN' if score == MAX_SCORE else 'needs a cleanse')
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
    sys.exit(0 if report(audit(text), allow_proof=allow_proof) == MAX_SCORE else 1)
