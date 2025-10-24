"""Data models for POE build scraping."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class SkillGem:
    """Represents a skill gem in a link group."""
    name: str
    is_support: bool = False


@dataclass
class SkillGroup:
    """Represents a group of linked gems."""
    gems: List[SkillGem] = field(default_factory=list)
    slot: Optional[str] = None  # e.g., "Body Armour", "Weapon"

    @property
    def main_skill(self) -> Optional[str]:
        """Get the main active skill gem."""
        for gem in self.gems:
            if not gem.is_support:
                return gem.name
        return None

    @property
    def link_count(self) -> int:
        """Number of linked gems."""
        return len(self.gems)

    def __repr__(self) -> str:
        main = self.main_skill or "Unknown"
        return f"SkillGroup({main} + {self.link_count-1} supports)"


@dataclass
class ItemSlot:
    """Represents an equipped item."""
    slot: str  # "Weapon", "Body Armour", "Helmet", etc.
    name: Optional[str] = None
    rarity: Optional[str] = None  # "Unique", "Rare", etc.

    def __repr__(self) -> str:
        return f"{self.slot}: {self.name or 'Empty'}"


@dataclass
class Build:
    """Represents a single build from poe.ninja."""

    # Identity
    character_name: str
    rank: int  # Position in ladder

    # Core stats
    level: int
    ascendancy: str  # e.g., "Berserker", "Juggernaut"

    # Defensive stats
    life: int
    energy_shield: int
    effective_hp: int  # Parsed from "63k" -> 63000

    # Offensive stats
    dps: int  # Parsed from "1.3M" -> 1300000
    main_skill: str  # Extracted from gem image filename

    # Build characteristics
    keystones: List[str] = field(default_factory=list)  # ["Resolute Technique", ...]

    # Detailed build info (populated from detail page)
    skill_groups: List[SkillGroup] = field(default_factory=list)
    items: List[ItemSlot] = field(default_factory=list)

    # Metadata
    profile_url: str = ""  # Link to poe.ninja build details page
    account_name: Optional[str] = None  # May be extracted from profile URL

    def __repr__(self) -> str:
        return (
            f"Build(rank={self.rank}, name={self.character_name}, "
            f"level={self.level}, ascendancy={self.ascendancy}, "
            f"life={self.life}, ehp={self.effective_hp}, dps={self.dps})"
        )


@dataclass
class BuildSnapshot:
    """Collection of builds with metadata."""

    # Query parameters
    league: str  # "mercenarieshcssf"
    snapshot: str  # "hour-3", "day-1", "week-1", "latest"

    # Data
    builds: List[Build] = field(default_factory=list)
    total_builds: int = 0

    # Filters applied (for tracking)
    ascendancy_filter: Optional[str] = None
    min_level: Optional[int] = None
    max_level: Optional[int] = None

    # Metadata
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    scraper_version: str = "0.1.0"

    def __repr__(self) -> str:
        return (
            f"BuildSnapshot(league={self.league}, snapshot={self.snapshot}, "
            f"builds={len(self.builds)}, scraped_at={self.scraped_at})"
        )

    def filter_by_ascendancy(self, ascendancy: str) -> "BuildSnapshot":
        """Return a new snapshot filtered by ascendancy."""
        filtered_builds = [b for b in self.builds if b.ascendancy == ascendancy]
        return BuildSnapshot(
            league=self.league,
            snapshot=self.snapshot,
            builds=filtered_builds,
            total_builds=len(filtered_builds),
            ascendancy_filter=ascendancy,
            scraped_at=self.scraped_at,
            scraper_version=self.scraper_version,
        )

    def filter_by_level(
        self, min_level: Optional[int] = None, max_level: Optional[int] = None
    ) -> "BuildSnapshot":
        """Return a new snapshot filtered by level range."""
        filtered_builds = self.builds
        if min_level is not None:
            filtered_builds = [b for b in filtered_builds if b.level >= min_level]
        if max_level is not None:
            filtered_builds = [b for b in filtered_builds if b.level <= max_level]

        return BuildSnapshot(
            league=self.league,
            snapshot=self.snapshot,
            builds=filtered_builds,
            total_builds=len(filtered_builds),
            ascendancy_filter=self.ascendancy_filter,
            min_level=min_level,
            max_level=max_level,
            scraped_at=self.scraped_at,
            scraper_version=self.scraper_version,
        )

    def top(self, n: int) -> List[Build]:
        """Return top N builds."""
        return self.builds[:n]
