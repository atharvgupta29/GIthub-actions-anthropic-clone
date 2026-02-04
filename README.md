# Claude AI PR Reviewer

This repository demonstrates an automated GitHub Actions–based
pull request reviewer powered by Anthropic Claude.

On every pull request, the workflow:
- Extracts the PR diff
- Sends it to Claude for analysis
- Posts a structured review comment on the PR

Intended for research and internal tooling experimentation.
