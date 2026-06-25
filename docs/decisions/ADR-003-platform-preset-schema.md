# ADR #3 — Typed platform preset schema over freeform user input

**Date:** 2024  
**Status:** Accepted

## Context

Users need to specify which platforms they want outputs for, and each platform
has specific dimension requirements. We needed to decide how to handle this.

## Decision

Define a typed `PLATFORM_PRESETS` dictionary in the API as the single source of
truth. The frontend mirrors these in a TypeScript config. Users select from a
fixed list; they cannot input arbitrary dimensions.

## Reasoning

Freeform dimension input creates a large surface area for invalid configurations
reaching the processing pipeline (zero dimensions, negative values, extreme
aspect ratios). A fixed preset list eliminates this class of error entirely.

It also makes the UI self-documenting — users see platform names, not pixel
values — and ensures our output quality guarantees are maintained per platform.

When platform requirements change (e.g. Bluesky changes its size limit), there
is one place to update rather than hunting down validation logic.

## Alternatives Considered

**Freeform width/height inputs:** Rejected. Too much validation surface area,
poor UX (users shouldn't need to know pixel dimensions), and harder to maintain.

**User-defined presets (save your own):** Good future feature, but out of scope
for v1. The fixed preset schema makes it easy to add this later — custom presets
would simply be additional entries in the same shape.

## Consequences

- Platform list is opinionated and curated — adding a new platform requires a
  code change and deployment
- TypeScript types on the frontend must be kept in sync with Python presets
  (manual for now; could be automated via openapi-typescript in future)
- Users cannot generate arbitrary dimensions — this is intentional
