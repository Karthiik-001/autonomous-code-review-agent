# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all
operations.

## Conventions

- Create an issue: `gh issue create --title "..." --body "..."`
- Read an issue: `gh issue view <number> --json number,title,body,labels,comments`
- List issues: `gh issue list --state open`
- Comment on an issue: `gh issue comment <number> --body "..."`
- Apply or remove labels: `gh issue edit <number> --add-label "..."` /
  `--remove-label "..."`
- Close an issue: `gh issue close <number> --comment "..."`

Infer the repository from the Git remote; `gh` does this automatically inside the
clone.

## Pull requests as a triage surface

**PRs as a request surface: no.**

When a skill says to publish to the issue tracker, create a GitHub issue. When it
says to fetch a relevant ticket, read it with `gh issue view <number> --comments`.
