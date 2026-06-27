"""
Core image processing functions.

Ported directly from the original folder-watcher script into
stateless, testable functions. No file I/O here — everything
works on PIL Image objects so the API layer controls I/O.
"""

import os
import cv2
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.presets import PlatformPreset


# ---------------------------------------------------------------------------
# Crop + resize
# ---------------------------------------------------------------------------

def crop_to_aspect(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Centre-crop img to match the target aspect ratio."""
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))

    return img


def resize_for_platform(img: Image.Image, preset: PlatformPreset) -> Image.Image:
    """Crop to aspect ratio then resize to exact platform dimensions."""
    cropped = crop_to_aspect(img, preset.width, preset.height)
    return cropped.resize((preset.width, preset.height), Image.LANCZOS)


# ---------------------------------------------------------------------------
# Watermark
# ---------------------------------------------------------------------------

def add_watermark(
    img: Image.Image,
    text: str,
    font_path: str | None = None,
    opacity: int = 180,
    padding: int = 20,
) -> Image.Image:
    """Composite a semi-transparent text watermark onto the bottom-right corner."""
    watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    font_size = int(min(img.size) * 0.04)
    try:
        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    except (IOError, OSError):
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = img.size[0] - text_w - padding
    y = img.size[1] - text_h - padding

    draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))
    return Image.alpha_composite(img.convert("RGBA"), watermark_layer).convert("RGB")


# ---------------------------------------------------------------------------
# Content moderation
# ---------------------------------------------------------------------------

class ModerationMode:
    OFF = "off"
    BLUR = "blur"
    STICKER = "sticker"


MODERATION_TARGET_LABELS = {
    "MALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_COVERED",
    "ANUS_EXPOSED",
    "ANUS_COVERED",
    "BUTTOCKS_EXPOSED",
}


def _apply_blur(img_pil: Image.Image, boxes: list[tuple], intensity: int = 25) -> Image.Image:
    img_array = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    for (x1, y1, x2, y2) in boxes:
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(img_array.shape[1], int(x2)), min(img_array.shape[0], int(y2))
        if x2 <= x1 or y2 <= y1:
            continue
        kernel = intensity if intensity % 2 == 1 else intensity + 1
        img_array[y1:y2, x1:x2] = cv2.GaussianBlur(
            img_array[y1:y2, x1:x2], (kernel, kernel), 0
        )

    return Image.fromarray(cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB))


def _apply_sticker(
    img_pil: Image.Image, boxes: list[tuple], sticker_path: str
) -> Image.Image:
    if not os.path.exists(sticker_path):
        return _apply_blur(img_pil, boxes)  # graceful fallback

    sticker = Image.open(sticker_path).convert("RGBA")
    img_out = img_pil.convert("RGBA")

    for (x1, y1, x2, y2) in boxes:
        x1, y1 = max(0, int(x1)), max(0, int(y1))
        x2, y2 = min(img_pil.width, int(x2)), min(img_pil.height, int(y2))
        region_w, region_h = x2 - x1, y2 - y1
        if region_w <= 0 or region_h <= 0:
            continue

        scale = max(region_w / sticker.width, region_h / sticker.height)
        scaled = sticker.resize(
            (int(sticker.width * scale), int(sticker.height * scale)), Image.LANCZOS
        )
        paste_x = x1 - (scaled.width - region_w) // 2
        paste_y = y1 - (scaled.height - region_h) // 2
        img_out.paste(scaled, (paste_x, paste_y), scaled)

    return img_out.convert("RGB")


def apply_moderation(
    img: Image.Image,
    mode: str,
    sticker_path: str | None = None,
    score_threshold: float = 0.5,
    blur_intensity: int = 25,
) -> tuple[Image.Image, list[dict]]:
    """
    Detect and optionally cover targeted regions.

    Returns (processed_image, detections) so callers can surface
    detection metadata to the frontend for preview mode.
    """
    if mode == ModerationMode.OFF:
        return img, []

    try:
        from imgutils.detect.nudenet import detect_with_nudenet
        raw = detect_with_nudenet(img, score_threshold=score_threshold)
    except Exception as e:
        # Don't crash the whole request if detection fails
        return img, [{"error": str(e)}]

    filtered = [
        {"box": box, "label": label, "score": round(score, 3)}
        for (box, label, score) in raw
        if label in MODERATION_TARGET_LABELS
    ]

    if not filtered:
        return img, []

    boxes = [d["box"] for d in filtered]

    if mode == ModerationMode.STICKER and sticker_path:
        return _apply_sticker(img, boxes, sticker_path), filtered
    else:
        return _apply_blur(img, boxes, blur_intensity), filtered


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def image_to_bytes(img: Image.Image, format: str = "JPEG", quality: int = 95) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=format, quality=quality)
    return buf.getvalue()
