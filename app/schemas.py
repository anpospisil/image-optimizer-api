"""
Request and response schemas.

Keeping these in a dedicated file makes it easy to generate
an OpenAPI-compatible TypeScript client later (via openapi-typescript).
"""

from pydantic import BaseModel, Field
from typing import Literal


class ProcessingConfig(BaseModel):
    """
    Configuration sent alongside the image upload.

    The frontend sends this as a JSON string in the multipart form
    field named 'config'.
    """

    platforms: list[str] = Field(
        ...,
        description="List of platform preset keys to generate outputs for.",
        example=["bluesky_square", "twitter_landscape", "pixiv"],
    )
    moderation_mode: Literal["off", "blur", "sticker"] = Field(
        default="off",
        description="Content moderation mode. 'off' skips detection entirely.",
    )
    watermark_text: str | None = Field(
        default=None,
        description="Text to composite onto each output. Omit to skip watermarking.",
        example="@yourhandle",
    )
    preview_only: bool = Field(
        default=False,
        description=(
            "If true, run detection and return bounding boxes without "
            "applying moderation or generating outputs. Used for the "
            "preview mode UI."
        ),
    )
    score_threshold: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="NudeNet confidence threshold. Lower = more detections.",
    )
    blur_intensity: int = Field(
        default=25,
        ge=1,
        le=99,
        description="Gaussian blur kernel size. Only used when moderation_mode='blur'.",
    )


class DetectionResult(BaseModel):
    label: str
    score: float
    box: list[float]  # [x1, y1, x2, y2]


class ProcessedOutput(BaseModel):
    platform_key: str
    platform_label: str
    width: int
    height: int
    filename: str


class ProcessResponse(BaseModel):
    """
    Returned for normal (non-preview) processing requests.
    The actual image files are returned as a ZIP via StreamingResponse —
    this metadata object is embedded in a response header for the frontend.
    """

    outputs: list[ProcessedOutput]
    detections: list[DetectionResult]
    detection_count: int
    moderation_applied: bool


class PreviewResponse(BaseModel):
    """Returned when preview_only=true. No images processed."""

    detections: list[DetectionResult]
    detection_count: int
    image_width: int
    image_height: int
