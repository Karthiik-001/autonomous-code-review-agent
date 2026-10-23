# Domain docs

## Before exploring, read these

- `GLOSSARY.md` at the repository root, if it exists.
- `docs/adr/`, reading ADRs that touch the area being changed.

If these files do not exist, proceed silently. The domain-modeling skill creates
them lazily when terms or decisions are resolved.

## Use the glossary vocabulary

When naming a domain concept in an issue, refactor proposal, hypothesis, or test,
use the term defined in `GLOSSARY.md`. If a needed concept is not defined, treat
that as a signal for domain modeling rather than inventing conflicting
terminology.

## Flag ADR conflicts

If an output contradicts an existing ADR, surface the conflict explicitly instead
of silently overriding it.

## File structure

This is a single-context repository:

```text
/
├── GLOSSARY.md
├── docs/adr/
└── src/
```
