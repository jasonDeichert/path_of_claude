# Scraper Design & Implementation Plan

## Investigation Summary

### poe.ninja URL Structure
- **Base URL**: `https://poe.ninja/builds/{league}`
- **Time parameter**: `?timemachine=week-1` (week-2, week-3, etc.)
  - "Latest snapshot" = no timemachine parameter
  - Available: week-1 through week-18+ (depending on league age)
- **League identifiers**:
  - `mercenarieshcssf` (HC SSF Mercenaries)
  - `mercenarieshc` (HC Mercenaries)
  - `mercenariesssf` (SSF Mercenaries)
  - `mercenaries` (SC Trade Mercenaries)
  - etc.

### Table Structure
Table displays 100 builds per page with these columns:

| Column | Data | Extraction Method |
|--------|------|-------------------|
| Name | Character name | Text content of link |
| Level | Level + Ascendancy icon | Number + img alt attribute |
| Life | Life pool | Text content |
| ES | Energy Shield | Text content |
| EHP | Effective HP | Text content (with k/M suffix) |
| DPS | DPS + Main skill icon | Number + img src (gem image) |
| Keystones | Keystone icons | img alt attributes (multiple) |

**Key Insight**: All data is embedded in table rows - no need to click into individual builds!

## Data Model

```python
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Build:
    """Represents a single build from poe.ninja"""

    # Identity
    character_name: str
    account_name: Optional[str]  # May need to extract from profile link

    # Core stats
    level: int
    ascendancy: str  # e.g., "Berserker", "Juggernaut"

    # Defensive stats
    life: int
    energy_shield: int
    effective_hp: int  # Parse "63k" -> 63000

    # Offensive stats
    dps: int  # Parse "1.3M" -> 1300000
    main_skill: str  # Extract from gem image filename

    # Build characteristics
    keystones: List[str]  # ["Resolute Technique", "Iron Reflexes"]

    # Metadata
    rank: int  # Position in ladder (1-100 for first page)
    profile_url: str  # Link to poe.ninja build details

@dataclass
class BuildSnapshot:
    """Collection of builds with metadata"""

    # Query parameters
    league: str  # "mercenarieshcssf"
    snapshot: str  # "week-1", "latest", etc.

    # Filters applied (for future use)
    ascendancy_filter: Optional[str] = None
    min_level: Optional[int] = None
    max_level: Optional[int] = None

    # Data
    builds: List[Build]
    total_builds: int

    # Metadata
    scraped_at: str  # ISO timestamp
    scraper_version: str  # For tracking changes
```

## Scraper API Design

### High-Level Interface

```python
class PoeNinjaScraper:
    """
    Scrapes build data from poe.ninja with flexible parameterization.

    Design Goals:
    - Easy to specify league, snapshot, filters
    - Returns structured data (BuildSnapshot)
    - Handles pagination/loading automatically
    - Caches to avoid repeated requests
    """

    def scrape_builds(
        self,
        league: str,
        snapshot: str = "latest",
        ascendancy: Optional[str] = None,
        min_level: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> BuildSnapshot:
        """
        Scrape builds from poe.ninja.

        Args:
            league: League identifier (e.g., "mercenarieshcssf")
            snapshot: Time snapshot ("latest", "week-1", "week-2", etc.)
            ascendancy: Filter by ascendancy (e.g., "Berserker")
            min_level: Minimum character level
            limit: Max number of builds to scrape (default: all visible)

        Returns:
            BuildSnapshot with builds and metadata
        """
        pass

    def get_available_snapshots(self, league: str) -> List[str]:
        """
        Get list of available time snapshots for a league.

        Returns: ["latest", "week-1", "week-2", ..., "week-18"]
        """
        pass

    def export_pob_codes(
        self,
        builds: List[Build],
        output_dir: str = "builds/pob_exports"
    ) -> Dict[str, str]:
        """
        Extract POB codes for specific builds (Phase 2: Deep Dive).

        Navigates to each build's detail page and extracts the POB import code.

        Args:
            builds: List of Build objects to get POB codes for
            output_dir: Directory to save POB code files

        Returns:
            Dict mapping character_name -> pob_code (base64 string)
        """
        pass

    def export_pob_code(self, build: Build) -> str:
        """
        Get POB code for a single build.

        Args:
            build: Build object with profile_url populated

        Returns:
            Base64-encoded POB import code
        """
        pass
```

### Usage Examples

#### Phase 1: Quick Meta Overview

```python
scraper = PoeNinjaScraper()

# Get current meta for HC SSF
snapshot = scraper.scrape_builds(
    league="mercenarieshcssf",
    snapshot="latest"
)

# Get week 1 meta for comparison
week1 = scraper.scrape_builds(
    league="mercenarieshcssf",
    snapshot="week-1"
)

# Filter for specific ascendancy
berserkers = scraper.scrape_builds(
    league="mercenarieshcssf",
    snapshot="week-1",
    ascendancy="Berserker"
)

# Get high-level builds only
endgame = scraper.scrape_builds(
    league="mercenarieshcssf",
    snapshot="latest",
    min_level=95
)
```

#### Phase 2: Deep Dive with POB Exports

```python
# Get top builds from table
snapshot = scraper.scrape_builds(
    league="mercenarieshcssf",
    snapshot="week-1",
    ascendancy="Berserker"
)

# Export POB codes for top 10 builds
top_10 = snapshot.builds[:10]
pob_codes = scraper.export_pob_codes(top_10)

# Now you have POB codes that can be:
# 1. Imported into Path of Building desktop app
# 2. Decoded to XML for programmatic analysis
# 3. Saved for later comparison

# Example: Save for later analysis
for char_name, pob_code in pob_codes.items():
    with open(f'builds/pob_exports/{char_name}.txt', 'w') as f:
        f.write(pob_code)
```

#### Complete Workflow

```python
# Step 1: Scrape table data from multiple snapshots
week1 = scraper.scrape_builds("mercenarieshcssf", "week-1")
week4 = scraper.scrape_builds("mercenarieshcssf", "week-4")

# Step 2: Filter for promising builds
# (e.g., level 95+, Berserker, high EHP)
promising = [
    b for b in week1.builds
    if b.level >= 95 and b.ascendancy == "Berserker" and b.effective_hp > 50000
]

# Step 3: Get detailed POB data for analysis
pob_codes = scraper.export_pob_codes(promising[:5])

# Step 4: Analyze (manually or programmatically)
# - Import into POB desktop app
# - Or decode and parse the XML for automated analysis
```

## Implementation Strategy

### Phase 1: Table Scraping (MVP)
**Goal**: Get overview of top builds with filtering capability

1. Load page with league + snapshot params
2. Extract all visible table rows (100 builds)
3. Parse each row for:
   - Name, level, life, ES, EHP, DPS
   - Ascendancy (from img alt)
   - Main skill (from img src -> parse gem name)
   - Keystones (from img alt)
   - Profile URL (href from name link)
4. Return BuildSnapshot with metadata
5. Apply client-side filters (ascendancy, min level, etc.)

**Implementation Detail**:
- URL: `https://poe.ninja/builds/{league}?timemachine={snapshot}`
- Table selector: `tbody tr`
- Extract: name, level + ascendancy icon, stats, skill gem icon, keystones

### Phase 2: POB Export Extraction
**Goal**: Get detailed build data for top N builds

1. Take filtered list of promising builds
2. For each build:
   - Navigate to profile URL
   - Wait for page load
   - Extract POB code from: `input[aria-label*="Path of Building"]` value attribute
3. Return dict of {character_name: pob_code}
4. Optionally save to files in `builds/pob_exports/`

**Implementation Detail**:
- POB codes are base64-encoded strings starting with "eN"
- ~9000-15000 characters per build
- Can be directly imported into POB desktop app
- Can be decoded to XML for programmatic analysis

### Phase 3: Filtering & Ranking
- Client-side filtering (filter after Phase 1 scraping)
- Ranking strategies:
  - By level (proxy for build success)
  - By EHP (survivability)
  - By ascendancy popularity
- Future: Could use poe.ninja's own filters if they update URLs

### Phase 4: Caching
- Cache scraped data locally
- Don't re-scrape same (league, snapshot) within X hours
- Store table data in `data/cache/{league}_{snapshot}.json`
- Store POB codes in `builds/pob_exports/{char_name}.txt`

## Output Format

### JSON Structure
```json
{
  "league": "mercenarieshcssf",
  "snapshot": "week-1",
  "scraped_at": "2025-10-23T22:00:00Z",
  "scraper_version": "0.1.0",
  "filters": {
    "ascendancy": null,
    "min_level": null
  },
  "total_builds": 100,
  "builds": [
    {
      "rank": 1,
      "character_name": "NeraFuarkLeGoat",
      "level": 100,
      "ascendancy": "Berserker",
      "life": 6240,
      "energy_shield": 27,
      "effective_hp": 63000,
      "dps": 1300000,
      "main_skill": "Spike Slam",
      "keystones": ["Resolute Technique"],
      "profile_url": "https://poe.ninja/builds/mercenarieshcssf/character/..."
    }
  ]
}
```

### File Naming Convention
`builds/{league}_{snapshot}_{timestamp}.json`

Examples:
- `builds/mercenarieshcssf_latest_20251023.json`
- `builds/mercenarieshcssf_week-1_20251023.json`
- `builds/mercenarieshcssf_week-2_20251023.json`

## Key Implementation Details

### Parsing Helpers

```python
def parse_number_with_suffix(value: str) -> int:
    """Parse "63k" -> 63000, "1.3M" -> 1300000"""
    value = value.strip().upper()
    if value.endswith('K'):
        return int(float(value[:-1]) * 1000)
    elif value.endswith('M'):
        return int(float(value[:-1]) * 1000000)
    else:
        return int(value)

def extract_skill_name_from_url(url: str) -> str:
    """
    Extract skill name from gem image URL.

    Input: "https://web.poecdn.com/.../SpikeSlamGem.png"
    Output: "Spike Slam"
    """
    # Extract filename
    filename = url.split('/')[-1].replace('.png', '')
    # Remove "Gem" suffix
    skill_name = filename.replace('Gem', '')
    # Add spaces before capitals (SpikeSl am -> Spike Slam)
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', skill_name)
```

### Error Handling

- **Page load failures**: Retry with exponential backoff
- **Missing data**: Log warning, use None/empty values
- **Parsing errors**: Skip build, log error, continue
- **Rate limiting**: Add delays between requests

## Testing Strategy

1. **Unit tests**: Test parsing helpers
2. **Integration tests**:
   - Scrape known league/snapshot
   - Verify data structure
   - Check that at least N builds returned
3. **Regression tests**:
   - Save snapshot of scraped data
   - Re-run scraper, compare structure

## Next Steps

1. Implement `Build` and `BuildSnapshot` dataclasses
2. Implement basic scraper (Phase 1 MVP)
3. Add CLI for testing: `python scrape.py mercenarieshcssf week-1`
4. Validate output against manual inspection
5. Add filtering and caching (Phases 2-4)

---

*This design prioritizes flexibility and ease of use for build analysis workflows.*
