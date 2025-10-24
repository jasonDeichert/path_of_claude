"""Parsing utilities for extracting build data from poe.ninja."""

import re
from typing import Optional


def parse_number_with_suffix(value: str) -> int:
    """
    Parse numbers with k/M suffixes to integers.

    Examples:
        "63k" -> 63000
        "1.3M" -> 1300000
        "5240" -> 5240
        "Any" -> 0
    """
    if not value or value.strip().lower() in ["any", "", "-"]:
        return 0

    value = value.strip().upper()

    try:
        if value.endswith("K"):
            return int(float(value[:-1]) * 1000)
        elif value.endswith("M"):
            return int(float(value[:-1]) * 1000000)
        else:
            # Remove commas if present
            value = value.replace(",", "")
            return int(value)
    except (ValueError, AttributeError):
        return 0


def extract_skill_name_from_url(url: str) -> str:
    """
    Extract skill name from gem image URL.

    Examples:
        "https://web.poecdn.com/.../SpikeSlamGem.png" -> "Spike Slam"
        ".../BoneshatterGem.png" -> "Boneshatter"
        ".../VortexOfProjectionGem.png" -> "Vortex Of Projection"
    """
    if not url:
        return "Unknown"

    # Extract filename from URL
    filename = url.split("/")[-1]

    # Remove .png extension
    filename = filename.replace(".png", "")

    # Remove "Gem" suffix if present
    if filename.endswith("Gem"):
        filename = filename[:-3]

    # Add spaces before capital letters (SpikeSl am -> Spike Slam)
    # But be careful with consecutive capitals (like "Of" in "VortexOfProjection")
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", filename)

    # Handle consecutive capitals (e.g., "VortexO fProjection" -> "Vortex Of Projection")
    spaced = re.sub(r"([A-Z])([A-Z][a-z])", r"\1 \2", spaced)

    return spaced.strip()


def extract_account_from_url(profile_url: str) -> Optional[str]:
    """
    Extract account name from profile URL.

    Example:
        "/builds/mercenarieshcssf/character/neradus94-0540/NeraFuarkLeGoat?..."
        -> "neradus94-0540"
    """
    if not profile_url:
        return None

    parts = profile_url.split("/")
    try:
        # URL format: /builds/{league}/character/{account}/{character}
        character_idx = parts.index("character")
        return parts[character_idx + 1]
    except (ValueError, IndexError):
        return None


def clean_keystone_name(name: str) -> str:
    """
    Clean keystone name from image alt text.

    Usually they're already clean, but just in case.
    """
    return name.strip()
