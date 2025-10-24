# POE.ninja Builds Scraper

Two-phase scraper for extracting build data from poe.ninja:
- **Phase 1**: Table scraping for build overview
- **Phase 2**: POB export extraction for detailed analysis

## Features

✅ Extract build data from poe.ninja builds table
✅ Support for hour, day, and week snapshots
✅ Filter by ascendancy, level range
✅ Export POB codes for detailed analysis
✅ Save snapshots to JSON
✅ CLI tool with multiple options

## Quick Start

```bash
# Install dependencies (from repo root)
pip install -r requirements.txt
playwright install chromium

# Scrape top 20 builds from hour-3 snapshot
python scrape.py mercenarieshcssf hour-3 --limit 20

# Filter for specific ascendancy
python scrape.py mercenarieshcssf hour-3 --ascendancy Berserker

# Export POB codes for top 5 builds
python scrape.py mercenarieshcssf hour-3 --ascendancy Berserker --export-pob 5

# Save snapshot to JSON
python scrape.py mercenarieshcssf hour-3 --output builds/hour-3.json
```

## Available Snapshots

**Hour-based** (early league):
- `hour-3`, `hour-6`, `hour-12`, `hour-18`

**Day-based**:
- `day-1` through `day-6`

**Week-based**:
- `week-1` through `week-18+`

**Latest**:
- `latest` (current snapshot)

## Usage Examples

### Early League Progression Analysis

```python
from scraper import PoeNinjaScraper

scraper = PoeNinjaScraper()

# Get top Berserkers at different progression points
hour_3 = scraper.scrape_builds("mercenarieshcssf", "hour-3")
hour_6 = scraper.scrape_builds("mercenarieshcssf", "hour-6")
hour_12 = scraper.scrape_builds("mercenarieshcssf", "hour-12")

# Filter for Berserkers
berserkers_h3 = hour_3.filter_by_ascendancy("Berserker")
berserkers_h6 = hour_6.filter_by_ascendancy("Berserker")
berserkers_h12 = hour_12.filter_by_ascendancy("Berserker")

# Export POB codes for top 5
top_5_h12 = berserkers_h12.top(5)
pob_codes = scraper.export_pob_codes(top_5_h12, "builds/pob_exports/hour-12")
```

See `examples/early_league_progression.py` for a complete workflow.

## Data Model

### Build
```python
@dataclass
class Build:
    character_name: str
    rank: int
    level: int
    ascendancy: str
    life: int
    energy_shield: int
    effective_hp: int
    dps: int
    main_skill: str
    keystones: List[str]
    profile_url: str
    account_name: Optional[str]
```

### BuildSnapshot
```python
@dataclass
class BuildSnapshot:
    league: str
    snapshot: str
    builds: List[Build]
    total_builds: int
    ascendancy_filter: Optional[str]
    min_level: Optional[int]
    max_level: Optional[int]
    scraped_at: str
    scraper_version: str
```

## Architecture

See `docs/SCRAPER-DESIGN.md` for detailed design and implementation notes.
