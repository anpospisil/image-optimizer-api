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
    "instagram_square": PlatformPreset(
        label="Instagram (Square)",
        width=1080,
        height=1080,
        max_file_size_kb=8000,
        notes="1:1 feed post, the most universally safe crop for Instagram.",
    ),
    "instagram_portrait": PlatformPreset(
        label="Instagram (Portrait)",
        width=1080,
        height=1350,
        max_file_size_kb=8000,
        notes="4:5 feed post. Taller aspect gets more vertical space in-feed.",
    ),
    "instagram_story": PlatformPreset(
        label="Instagram (Story/Reel)",
        width=1080,
        height=1920,
        max_file_size_kb=8000,
        notes="9:16 full-screen format for Stories and Reels covers.",
    ),
    "facebook_square": PlatformPreset(
        label="Facebook (Square)",
        width=1080,
        height=1080,
        max_file_size_kb=8000,
        notes="1:1 for direct photo/feed posts.",
    ),
    "facebook_landscape": PlatformPreset(
        label="Facebook (Link Preview)",
        width=1200,
        height=630,
        max_file_size_kb=8000,
        notes="1.91:1 — the standard link-share preview size on Facebook.",
    ),
}
