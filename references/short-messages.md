# Short messages: the shape passes

The four-step loop scores what a sentence says. A short message going to one person fails
differently: the tell is whether the sentence should exist at all. The scorer's windows
and floors are tuned for pages, so it cannot see that failure, and the gap is not small.
Run the loop on this client reply and it ships clean:

```text
Hi Jennifer! Thanks so much for the kind words about the dashboard, really glad you're
enjoying it so far! To answer your questions: 1) Yes, I can absolutely update the header
color to match your brand blue, I will get that changed today. 2) Of course! I'd be happy
to add Sarah as a user, I will just need her email address. 3) Regarding the SMS piece,
we are still on track and I am expecting to have it ready by the end of next week. Let me
know if you have any other questions!
```

```shell
$ python3 tools/deslop.py --text "…the reply above…"
95 words of visible copy

  score 5/5  CLEAN
```

No banned word, no shape, no cadence the window can catch. Every line is still something
a busy human would never have typed: a greeting on an active thread, performed delight,
numbered answers that mirror the inbound point by point, equal word count on every item,
`I will` and `we are` left uncontracted throughout, and sign-off fluff at the end.

Nothing here replaces the loop. For a draft under roughly 150 words that is going to one
person, the three passes below run FIRST, then the loop runs on whatever survives, and the
contraction sweep runs last on the finished text. Cleanse after the shape passes, never
before: de-slopping the wording of a sentence that should not exist leaves a sentence that
should not exist.

## Pass 1 · Reply shape

The loudest structural tell in a reply: it treats the inbound message as a checklist. Every
point the sender made gets acknowledged, in their order, often restated before it is
answered. The reply can pass every word check and still read as a bot, because the tell is
the skeleton.

**Read the inbound message, not just the draft.** Mirroring is invisible without it. No
inbound in reach? Say so rather than scoring blind.

Tag what the sender sent, then build the reply from the answers up:

| They sent | You owe them |
|---|---|
| a question or a decision request | an answer. Three words is a valid answer |
| an obligation (money, scope, deadline) | it handled, folded into the answer or the next step |
| context | a response only if it changes what happens next |
| routine thanks or praise | nothing at all |
| a real apology, bad news, visible strain | one short human line, then move on |

Then shape it:

- Open on the answer to the biggest question. Not a greeting, not a reaction.
- Batch. One sentence that answers two questions beats two sentences.
- Spend length where the stakes are. The deal-critical question gets the words, the minor
  one gets three.
- At most one question back, the one that actually blocks you. A numbered list of questions
  back is an interrogation form.
- Make the call instead of offering a menu, unless the choice is genuinely theirs (money,
  scope, brand).
- The shape never overrides truth. If the answer is not known yet, say so plainly. A made-up
  specific is worse than any tell.

Mirror test on the finished draft. It has failed if it answers social points, restates
questions before answering them, tracks the inbound's structure, gives every point equal
weight, or is longer than the inbound without delivering anything new.

Banned skeletons: sectioning by their points (`Regarding X… As for Y…`), numbered answers
to prose, restate-then-answer (`You asked whether X. It does.`), and echoing their exact
phrasing on every mention. After the first mention a human compresses to `it`.

## Pass 2 · Hard cuts

Delete these outright. Do not reword them; a reword survives.

| Cut | Specimen |
|---|---|
| Greetings on an ongoing thread | `Hope you're doing well` |
| Narrated reactions | `Glad that landed well!` · `Awesome!` |
| Praise of the client or the question | `Great question` · `Love this` |
| Restating the question before answering it | they know what they asked |
| Unrequested reasoning and caveats | `Just so you know` · `I should mention` |
| Sign-off fluff | `Let me know if you have any questions` · `Hope that helps!` |
| Meta-narration of the act of messaging | `I wanted to reach out` · `I just wanted to follow up` |
| Recap endings | `To summarize, I'll have it by Friday`. The message already said Friday |
| Canned service phrases | `Thank you for your patience` · `Rest assured` |
| Naming the client's emotions | `I completely understand your frustration` |
| Explaining their project back to them | they know their own goals |
| Confession wrapped around a correction | ship the corrected fact, skip the apology |

The last row is the counterintuitive one. Correcting a fact and confessing to having been
wrong are two different acts, and only the first belongs in the message. The correction
already implies the earlier version was wrong; saying so out loud spends credibility the
reader was not questioning.

## Pass 3 · Sentence level

| Tell | Fix |
|---|---|
| A bare verdict delivered as pronouncement | own it: `I think that's the right call` |
| Conditional distance on your own intent | `I would suggest` → `I suggest` |
| A note labelled before it is given | `One honest note on cost:` → give the cost note |
| Balanced closers built for effect | `not because X but because Y` → say the plain reason |
| Subjectless fragments carrying a request | a person doing the thing: `I've attached the scope` |
| Troubleshooting narrated back | state what you did, cut the diagnosis |
| Greeting on an active thread | none at all, or a bare first name |

## The contraction sweep (always last)

The rewrite step of the loop asks for a rough edge, a contraction included. This is the
mechanical version, because an instruction to "add contractions" ships copy like `I will
get that changed today`. Search the finished message for every string on the left. Each
hit is a defect unless a guardrail covers it.

| Find | Write |
|---|---|
| I am · you are · we are · they are | I'm · you're · we're · they're |
| he is · she is · it is · that is | he's · she's · it's · that's |
| there is · here is · what is · who is | there's · here's · what's · who's |
| I will · you will · we will · they will | I'll · you'll · we'll · they'll |
| I would · you would · we would | I'd · you'd · we'd |
| I have · we have (helper verb) | I've · we've |
| do not · does not · did not | don't · doesn't · didn't |
| is not · are not · was not · were not | isn't · aren't · wasn't · weren't |
| have not · has not | haven't · hasn't |
| cannot · could not · would not · will not | can't · couldn't · wouldn't · won't |
| let us (do something) | let's |

Guardrails that keep the full form: real emphasis (`I *will* fix it today`), a verb that
ends the clause (`Yes, I will.`), genuinely legal copy, possessives (never touch `its` or
`your`), and `have` as ownership (`we have two vans` stays).

Never write: `gonna`, `wanna`, `gotta`, `ain't`, `y'all`, double contractions
(`wouldn't've`), or noun-plus-`ll` (`Sarah'll`).

## Curator voice

Register-level, and it survives every word check: the sentence that evaluates the reader's
experience for them, like a museum placard.

| Banned | Instead |
|---|---|
| `worth a look` · `worth pushing on` | name the thing, or `Try it.` |
| `feel free to` · `don't hesitate to` | say the thing |
| `the real test is` · `the interesting part is` | delete the frame, keep the fact |
| `take a look` · `give it a spin` · `see for yourself` | `Try it.` Or nothing |
| `that's where you can watch it hold` | what it does, then stop |

Never tell the reader what to notice, why it is impressive, or what it proves. Give them
the thing and how to use it. They draw the conclusion.

## The reply this file ships

```text
Header changes to brand blue today. Send me Sarah's email and I'll get her access. SMS is
on track for end of next week.
```

The praise got no reaction. Three questions became three short answers, none restated, none
numbered, every question still answered. Killing the mirror means killing the checklist
skeleton and the social echoes, never ghosting a real question.

The one test, on every line: would a competent contractor, thumbing this out between jobs,
actually type that sentence? When unsure, cut it. A message that feels slightly too short
to the writer is usually exactly right to the reader.
