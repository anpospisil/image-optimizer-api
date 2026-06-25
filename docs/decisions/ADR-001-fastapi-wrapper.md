# ADR #1 — Wrap Python in FastAPI rather than rewrite processing in Node

**Date:** 2024  
**Status:** Accepted

## Context

The image processing pipeline (crop, resize, watermark, content moderation) was
originally a Python script using PIL, OpenCV, and `dghs-imgutils` (a NudeNet wrapper).

When moving to a web architecture, we needed to decide whether to:
- Keep the Python logic and expose it via a FastAPI service
- Rewrite everything in Node.js (using Sharp for image processing)

## Decision

Wrap the existing Python in FastAPI. The Next.js frontend calls it as a microservice
over HTTP.

## Reasoning

The content moderation pipeline (`dghs-imgutils` / NudeNet) has no viable Node.js
equivalent. Rewriting it would mean either finding an inferior detection library or
maintaining a Python sidecar anyway — at which point we'd have two runtimes *and*
a rewrite. The image processing logic (PIL crop/resize/watermark) works correctly
and has already been validated against real images. Rewriting correct, working code
introduces risk with no functional gain.

Sharp (Node) is faster than PIL for pure resize operations, but performance is not
a bottleneck at our current scale. This is a candidate for a future optimisation
once the moderation pipeline is separated.

## Alternatives Considered

**Node.js + Sharp for everything:** Rejected. No NudeNet equivalent in Node.
Sharp is faster for resizing but the moderation rewrite risk is too high.

**Node.js + Python sidecar only for detection:** Viable but adds complexity.
Two runtimes plus a rewrite of the image processing. Deferred to a future ADR
if Sharp migration becomes worthwhile.

## Consequences

- Two runtimes to deploy and maintain (Vercel for Next.js, Railway for FastAPI)
- The FastAPI service must be kept running and health-checked
- The Next.js frontend must handle CORS and cross-origin ZIP downloads
- Future: if we migrate image processing to Sharp, this ADR should be revisited
  and the Python service scope reduced to detection-only
