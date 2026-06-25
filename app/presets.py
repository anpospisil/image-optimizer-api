"""
Platform preset definitions.

This is the single source of truth for all supported platforms.
The Next.js frontend will mirror these in a TypeScript config —
both should stay in sync. If you add a platform here, add it there too.

ADR #3: We use a typed preset schema rather than letting users input
arbitrary dimensions. This prevents invalid configs reaching the
processing pipeline and makes the UI self-documenting.
"""

from typing import NamedTuple


class PlatformPreset(NamedTuple):
    label: str       # Human-readable name for the UI
    width: int
    height: int
    max_file_size_kb: int  # Soft warning threshold, not enforced
    notes: str


PLATFORM_PRESETS: dict[str, PlatformPreset] = {
    "bluesky_square": PlatformPreset(
        label="Bluesky (Square)",
        width=1000,
        height=1000,
        max_file_size_kb=1000,
        notes="Primary discovery platform. Square performs best.",
    ),
    "bluesky_landscape": PlatformPreset(
        label="Bluesky (Landscape)",
        width=1200,
        height=675,
        max_file_size_kb=1000,
        notes="16:9 landscape for Bluesky.",
    ),
    "twitter_square": PlatformPreset(
        label="Twitter/X (Square)",
        width=900,
        height=900,
        max_file_size_kb=5000,
        notes="Square format for Twitter/X.",
    ),
    "twitter_landscape": PlatformPreset(
        label="Twitter/X (Landscape)",
        width=1200,
        height=675,
        max_file_size_kb=5000,
        notes="16:9 landscape for Twitter/X.",
    ),
    "pixiv": PlatformPreset(
        label="Pixiv",
        width=2048,
        height=2048,
        max_file_size_kb=32000,
        notes="Pixiv allows up to 32MB. 2048px longest side is the sweet spot for quality.",
    ),
    "fanbox": PlatformPreset(
        label="Pixiv Fanbox",
        width=2048,
        height=2048,
        max_file_size_kb=8000,
        notes="Fanbox has a tighter file size limit than Pixiv.",
    ),
}
