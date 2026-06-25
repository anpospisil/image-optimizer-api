# image-optimizer-api

FastAPI service powering the Image Optimizer. Handles image processing,
platform-specific resizing, watermarking, and optional content moderation.

## Architecture

This service is a deliberate wrapper around an existing Python processing
pipeline rather than a Node.js rewrite. See [ADR #1](docs/decisions/ADR-001-fastapi-wrapper.md)
for the reasoning.

```
Next.js frontend (Vercel)
        ↕ HTTP / multipart
FastAPI service (Railway)
  ├── app/main.py          — FastAPI app, CORS, router registration
  ├── app/presets.py       — Platform preset definitions (single source of truth)
  ├── app/processing.py    — Stateless image processing functions
  ├── app/schemas.py       — Pydantic request/response models
  └── app/routers/
      └── process.py       — POST /api/process, GET /api/presets
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/presets` | List all platform presets |
| POST | `/api/process` | Process an image |

### POST /api/process

**Form fields:**
- `image` — file upload (JPEG, PNG, WebP, max 50MB)
- `config` — JSON string matching `ProcessingConfig`

**Config shape:**
```json
{
  "platforms": ["bluesky_square", "twitter_landscape", "pixiv"],
  "moderation_mode": "off | blur | sticker",
  "watermark_text": "@yourhandle",
  "preview_only": false,
  "score_threshold": 0.01,
  "blur_intensity": 25
}
```

**Response (normal mode):** ZIP file stream with processed images.
Metadata available in `X-Process-Metadata` response header.

**Response (preview_only=true):** JSON with detection bounding boxes.
No images are processed or returned.

## Local development

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs` (Swagger UI).

## Deployment

Configured for Railway via `railway.toml`. Set environment variables
in the Railway dashboard — do not commit `.env`.

## Architecture decisions

- [ADR #1 — FastAPI wrapper over Node rewrite](docs/decisions/ADR-001-fastapi-wrapper.md)
- [ADR #3 — Typed platform preset schema](docs/decisions/ADR-003-platform-preset-schema.md)
