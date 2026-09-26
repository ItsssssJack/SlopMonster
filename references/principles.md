# Editing principles

Use these checks alongside the pattern catalogue. Start with the document's
reader and purpose, then review individual sentences. A passing checker score
does not answer the editorial questions below.

## 1. Give the reader the information they need

Identify what the reader came to learn or do. In a README, explain the project's
function before discussing optional integrations. In an email, state the reason
for writing early. A sales page may need to establish a customer problem before
describing the offer.

Steve Krug's *Don't Make Me Think* informs the emphasis on reducing unnecessary
interpretation. Problem-first pitch guidance from Daniel Priestley and Alex
Hormozi is useful for sales copy; it should not dictate every document's opening.

> Before: ~~It scores your copy out of 5 and it can fail your build.~~
>
> After: The checker reports matches in five categories. You can also run it in
> an automated repository check, where a score below 5/5 returns a failure status.

The second sentence supplies the context needed to understand the optional use.
Whether that failure blocks a merge or deployment depends on the configuration.

## 2. Make the opening lead into an explanation

A hook should establish a relevant question or reason to read. Once it has done
that, answer the question. Avoid following it with another vague promise about
information that appears later.

Read the first few paragraphs together. Check whether the reader learns something
useful in each one. Remove openings that could introduce almost any product.

> Before: ~~Most tools that fix this are built on the same public research. This
> one adds the two things the others skip.~~
>
> After: SlopMonster includes a Python checker and instructions for editing the
> draft with an AI agent.

The replacement explains the contents without making an unsupported comparison
with other tools.

## 3. Check the relationship between sentences

Each sentence should add information, explain a consequence or provide an example
the reader needs. Repeated metaphors and mirrored sentence structures can create
rhythm without developing the point.

Read adjacent sentences for meaning. Ask what the second sentence adds and whether
its claim follows from the first. Use a contrast only when the distinction matters.

> Before: ~~Developers call this a linter. Everyone else can call it a checker
> that will not let you ship.~~
>
> After: Run the checker on a file to see which patterns it flags. The command
> leaves the file unchanged.

The replacement describes what someone using the command can expect.

## 4. Keep claims within the available evidence

Use a specific detail when it is relevant and supported. Do not add a number or
testimonial merely to make a sentence feel concrete. Verify dates and technical
specifications as carefully as customer counts.

The roofing examples in [the worked example](../examples/ridgeline-roofing.md)
illustrate possible edits. A reader reusing them must check the underlying business
facts. A precise claim can still be false.

If necessary evidence is missing, mark the gap for the author. Describe limitations
and conditions where the claim appears so the reader can interpret it correctly.

## 5. Preserve a voice that suits the document

Read the edit aloud or as a complete page. Keep the author's level of formality and
allow sentence length to follow the content. Lists can have three items when there
are three useful items. An em dash can be appropriate punctuation.

Avoid imposing a quota of fragments or contractions. Do not invent an opinion or
deliberate error to make the writing seem personal. For instructions, prioritize
an order the reader can follow and commands they can use.

After editing, compare against the original for changed meaning and run the
checker again. Review remaining findings in context and report any necessary
exceptions. Never put ordinary prose in code formatting merely to suppress a match.
