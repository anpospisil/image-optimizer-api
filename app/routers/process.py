"""
/api/process — main image processing endpoint.

Two modes:
  1. preview_only=true  → detect regions, return bounding boxes, no output images
  2. preview_only=false → process + return ZIP of platform-optimised images
"""

import io
import json
import os
import zipfile
from datetime import datetime


from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image

from app.presets import PLATFORM_PRESETS
from app.processing import (
    ModerationMode,
    add_watermark,
    apply_moderation,
    image_to_bytes,
    resize_for_platform,
)
from app.schemas import (
    DetectionResult,
    PreviewResponse,
    ProcessedOutput,
    ProcessResponse,
    ProcessingConfig,
)

router = APIRouter()

SUPPORTED_FORMATS = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_MB = 50


@router.get("/presets")
def get_presets():
    """
    Return all available platform presets.
    The frontend calls this on mount to populate the platform selector.
    """
    return {
        key: {
            "label": preset.label,
            "width": preset.width,
            "height": preset.height,
            "max_file_size_kb": preset.max_file_size_kb,
            "notes": preset.notes,
        }
        for key, preset in PLATFORM_PRESETS.items()
    }


@router.post("/process")
async def process_image(
    image: UploadFile = File(..., description="Source image file (JPEG, PNG, or WebP)"),
    config: str = Form(..., description="JSON-encoded ProcessingConfig"),
):
    # --- Parse and validate config ---
    try:
        cfg = ProcessingConfig(**json.loads(config))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid config: {e}")

    # --- Validate file type ---
    if image.content_type not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{image.content_type}'. Use JPEG, PNG, or WebP.",
        )

    # --- Read and size-check the file ---
    raw_bytes = await image.read()
    size_mb = len(raw_bytes) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f}MB). Maximum is {MAX_FILE_SIZE_MB}MB.",
        )

    # --- Open image ---
    try:
        img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not open image: {e}")

    original_w, original_h = img.size


    # -----------------------------------------------------------------------
    # Preview mode — detect only, return bounding boxes, no output images
    # -----------------------------------------------------------------------
    if cfg.preview_only:
        if cfg.moderation_mode == ModerationMode.OFF:
            return JSONResponse(
                PreviewResponse(
                    detections=[],
                    detection_count=0,
                    image_width=original_w,
                    image_height=original_h,
                ).model_dump()
            )

        _, raw_detections = apply_moderation(
            img,
            mode=cfg.moderation_mode,
            sticker_path=os.getenv("STICKER_PATH", "assets/sticker.png"),
            score_threshold=cfg.score_threshold,
        )

        detections = [
            DetectionResult(
                label=d["label"],
                score=d["score"],
                box=list(d["box"]),
            )
            for d in raw_detections
            if "error" not in d
        ]

        return JSONResponse(
            PreviewResponse(
                detections=detections,
                detection_count=len(detections),
                image_width=original_w,
                image_height=original_h,
            ).model_dump()
        )


    # --- Validate requested platforms ---
    unknown = [p for p in cfg.platforms if p not in PLATFORM_PRESETS]
    if unknown:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown platform key(s): {unknown}. Call /api/presets for valid keys.",
        )
        

    # -----------------------------------------------------------------------
    # Full processing mode
    # -----------------------------------------------------------------------

    # Apply moderation once on the source image, before any resizing
    moderated_img = img
    all_detections: list[DetectionResult] = []

    if cfg.moderation_mode != ModerationMode.OFF:
        moderated_img, raw_detections = apply_moderation(
            img,
            mode=cfg.moderation_mode,
            sticker_path=os.getenv("STICKER_PATH", "assets/sticker.png"),
            score_threshold=cfg.score_threshold,
            blur_intensity=cfg.blur_intensity,
        )
        all_detections = [
            DetectionResult(
                label=d["label"],
                score=d["score"],
                box=list(d["box"]),
            )
            for d in raw_detections
            if "error" not in d
        ]

    # Generate per-platform outputs and stream as ZIP
    date_str = datetime.now().strftime("%Y%m%d")
    original_stem = image.filename.rsplit(".", 1)[0] if image.filename else "image"

    zip_buffer = io.BytesIO()
    outputs: list[ProcessedOutput] = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for platform_key in cfg.platforms:
            preset = PLATFORM_PRESETS[platform_key]
            processed = resize_for_platform(moderated_img, preset)

            if cfg.watermark_text:
                processed = add_watermark(processed, cfg.watermark_text)

            filename = f"{original_stem}_{date_str}_{platform_key}.jpg"
            zf.writestr(filename, image_to_bytes(processed))

            outputs.append(
                ProcessedOutput(
                    platform_key=platform_key,
                    platform_label=preset.label,
                    width=preset.width,
                    height=preset.height,
                    filename=filename,
                )
            )

    zip_buffer.seek(0)

    # Embed metadata as a response header so the frontend can read it
    # without parsing the ZIP (used to update UI state after download)
    metadata = ProcessResponse(
        outputs=outputs,
        detections=all_detections,
        detection_count=len(all_detections),
        moderation_applied=cfg.moderation_mode != ModerationMode.OFF,
    )

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{original_stem}_{date_str}.zip"',
            "X-Process-Metadata": metadata.model_dump_json(),
            "Access-Control-Expose-Headers": "X-Process-Metadata",
        },
    )
