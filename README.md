# image-optimizer-api

FastAPI service powering the Image Optimizer. Handles image processing,
platform-specific resizing, watermarking, and optional content moderation.

**API docs:** https://image-optimizer-api-0r7m.onrender.com/docs

---

## Architecture

This service is a deliberate wrapper around an existing Python processing
pipeline rather than a Node.js rewrite. See [ADR #1](docs/decisions/ADR-001-fastapi-wrapper.md)
for the reasoning.

The Next.js frontend (Vercel) communicates via HTTP multipart with this FastAPI service (Render):

    app/main.py          — FastAPI app, CORS, router registration
    app/presets.py       — Platform preset definitions (single source of truth)
    app/processing.py    — Stateless image processing functions
    app/schemas.py       — Pydantic request/response