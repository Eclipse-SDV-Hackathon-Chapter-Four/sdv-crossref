# Conventions for design-pattern research agents

> The brief the design cards were written under, kept so contributors (human or agent) can match the style.

- Vault root: the folder that holds README.md. Read first: _templates/pattern.md (the card shape), design/design-index.md (the lens), design/identity-discovery/instance-in-the-name-type-in-the-hash.md (the exemplar card), synthesis/gap-register.md (to fill `gap-rows:`), and the overview notes of the components your cluster touches (components/<slug>/<slug>-overview.md).
- Write 8–12 cards into design/<your-cluster>/<slug>.md. Basenames must be unique vault-wide: run `ls design/*/ components/*/ event/ synthesis/ playbook/` and avoid collisions. Slugs are the rule, not the topic ("announce-on-arrival-not-on-request", not "discovery").
- A card is one screen. Every section of the template is mandatory, including "For a hackathon team" and "Evidence". Prior-art tables need 3–7 rows, each a real standard, paper or system, with the primary source URL in `sources:`.
- Research with WebSearch and WebFetch against primary sources (specs, RFCs, project docs, papers). Do not invent prior art. Mark anything you could not verify "(unverified)".
- "On the Eclipse SDV stack" must name concrete seams in this vault's components (service names, attributes, manifests, resources, endpoints) and wiki-link the component notes. Fill `applies-to:` with component slugs and `gap-rows:` with ids from synthesis/gap-register.md (e.g. B2, H3). If a pattern justifies a gap nobody listed, say so in Evidence; do not edit the gap register.
- Patterns, not summaries: a reader should be able to apply the rule tomorrow. Prefer rules with a trap and a counter-example.
- Do not edit any file outside your design/<cluster>/ folder, except appending terms to glossary.md (format: `**TERM** — definition. [[note]]`).
- Final report (under 300 words): the list of cards (title + one line each), and 3–5 findings that contradict or sharpen an existing vault note (name the note).
