# Contributing to SiteSignal

SiteSignal is being implemented milestone by milestone from `OUTLINE/PHASE_1_OUTLINE.md`. Keeping changes small, reviewable, and aligned with the current milestone.

## Python runtime

SiteSignal currently uses Python 3.13.

- `.python-version` pins the local development interpreter.
- `pyproject.toml` defines the supported Python range.
- Do not change either version without documenting the reason in `decisions.md`.

## Branch workflow

Commits should be small, scoped, and written in the imperative mood.

Do not commit feature work directly to `main`.

Create a short-lived branch from the latest `main`:

```text
feature/<descriptive-name>
fix/<descriptive-name>
docs/<descriptive-name>
