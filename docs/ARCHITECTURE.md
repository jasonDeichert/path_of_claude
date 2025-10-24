# Architecture

## Overview

This tool bridges three data sources:
1. **poe.ninja** - What players are actually playing (scraped)
2. **Path of Building** - Game mechanics and calculations (submodule)
3. **User's character** - Current build state (POB import)

## Key Design Decisions

### 1. Path of Building as Submodule

**Decision:** Use POB as git submodule, require Lua modules directly

**Why:**
- POB already has all game data (passive tree, gems, items, mechanics)
- POB calculation engine is battle-tested and maintained
- Automatic updates when POB releases new versions
- We don't maintain game data ourselves

**How:**
```bash
git submodule add https://github.com/PathOfBuildingCommunity/PathOfBuilding pob
```

Then in our Lua code:
```lua
package.path = package.path .. ";./pob/src/?.lua"
local Build = require("Classes.Build")
```

### 2. Playwright over API Reverse Engineering

**Decision:** Use Playwright to scrape poe.ninja rendered pages

**Why:**
- poe.ninja deliberately obscures API (protobuf)
- Playwright is simpler and more maintainable
- Works even if they change backend
- Can extract exactly what we see in browser

**Tradeoff:**
- Slower than direct API
- Requires browser runtime
- More fragile to UI changes

**Future:** Could add protobuf support if scraping becomes a bottleneck

### 3. Multi-Language: Python + Lua

**Decision:** Use right tool for each job
- **Python:** Web scraping (Playwright), CLI orchestration
- **Lua:** POB integration, calculations

**Why:**
- POB is Lua - requiring modules is natural
- Python is better for web scraping
- JSON as bridge format between them

**How it works:**
```
Python scraper → builds.json → Lua analyzer (uses POB) → results.json → Python CLI
```

## Data Flow

### Phase 1: Data Collection
```
poe.ninja → Playwright → JSON snapshot
```

Scraper navigates to league page, extracts table data, saves structured JSON.

### Phase 2: Analysis (Future)
```
JSON snapshot → Lua script → POB calculations → Enhanced data
```

Load POB modules, import build, run calculations, augment with real stats.

### Phase 3: Query (Future)
```
User query → Filter logic → Ranked results
```

Filter by ascendancy, items, skills, etc. Rank by relevance.

## File Structure

```
poe-build-intel/
├── pob/                          # Git submodule (unmodified POB)
│   ├── src/                      # POB Lua source
│   ├── data/                     # Game data files
│   └── ...
├── src/
│   ├── scraper/
│   │   ├── poe_builds_scraper.py # Playwright scraper
│   │   └── extractors.py        # Data extraction logic (future)
│   ├── pob-integration/          # Lua code
│   │   ├── init.lua             # Load POB modules
│   │   ├── calculate.lua        # Run calculations
│   │   └── export.lua           # Generate POB codes
│   └── analysis/                 # Analysis logic (future)
│       ├── filter.py            # Build filtering
│       └── compare.py           # Build comparison
├── cli/
│   └── main.py                  # CLI interface (future)
├── data/                        # Cached data
│   └── snapshots/               # League snapshots
├── docs/
│   ├── PROJECT-VISION.md
│   └── ARCHITECTURE.md (this file)
└── examples/
    └── 3.27-patch-notes-*.txt   # Reference data
```

## Technology Choices

### Scraping: Playwright
- **Pros:** Reliable, handles JS, sees what users see
- **Cons:** Slower, requires browser
- **Alternative:** Protobuf decoding (future optimization)

### POB Integration: Lua + Submodule
- **Pros:** Use POB directly, always up-to-date, full calc engine
- **Cons:** Multi-language complexity
- **Alternative:** Port to Python (❌ too much work)

### Data Format: JSON
- **Pros:** Language-agnostic, human-readable, widely supported
- **Cons:** Verbose for large datasets
- **Alternative:** SQLite (if data grows large)

### CLI: Python Click
- **Pros:** Good UX, easy arg parsing, cross-platform
- **Cons:** Could use Lua if we prefer single language
- **Alternative:** Lua CLI (consider later)

## POB Integration Details

### What We Get from POB

1. **Game Data** (`pob/data/`)
   - Passive tree (all nodes, positions, connections)
   - Skill gems (base damage, scaling, tags)
   - Items (uniques, bases, implicits)
   - Mechanics constants

2. **Calculation Engine** (`pob/src/Modules/`)
   - `CalcOffence.lua` - DPS calculations
   - `CalcDefence.lua` - EHP, mitigation, etc.
   - `CalcSetup.lua` - Flasks, buffs, config
   - All game mechanics properly modeled

3. **Build Management** (`pob/src/Classes/`)
   - `Build.lua` - Build import/export
   - `Item.lua` - Item parsing
   - `Skill.lua` - Skill setup

### How We Use It

```lua
-- Our code: src/pob-integration/calculate.lua
package.path = package.path .. ";./pob/src/?.lua"

local Build = require("Classes.Build")

function analyzeBuild(buildXML)
    local build = new("Build")
    build:LoadFromXML(buildXML)

    -- Use POB's calculation functions
    build.calcs:BuildOutput()

    -- Return calculated stats
    return {
        dps = build.calcs.output.TotalDPS,
        life = build.calcs.output.Life,
        es = build.calcs.output.EnergyShield,
        ehp = build.calcs.output.EffectiveLife,
        -- ... hundreds of stats available
    }
end
```

### Updating POB

When POB releases a new version:
```bash
cd pob
git pull origin master
cd ..
git add pob
git commit -m "Update POB to v2.x.x"
```

Our code should continue working (assuming stable API).

## Open Questions

1. **Rate Limiting:** How to avoid hammering poe.ninja?
   - Cache aggressively
   - Respect robots.txt
   - Add delays between requests

2. **Data Staleness:** How often to re-scrape?
   - Pre-league: Once
   - Early league (days 1-7): Daily
   - Mid-league: Weekly
   - Late league: As needed

3. **Storage:** JSON files vs SQLite?
   - Start with JSON (simple)
   - Move to SQLite if dataset grows large

4. **POB Version Compatibility:** What if POB API changes?
   - Pin to specific POB commit for stability
   - Test before updating submodule
   - Version our code to match POB versions

## Future Considerations

### Performance Optimization
- Cache POB calculations (same build = same stats)
- Parallel processing for batch analysis
- Consider protobuf decoder for faster scraping

### Advanced Features
- Character import from POE API
- Build evolution tracking (same char over time)
- Meta shift detection (anomaly detection)
- "Builds I can play" matching algorithm

### Distribution
- Package as single executable (PyInstaller)
- Docker container (includes browser + Lua runtime)
- Web interface (future, maybe)

---

*This architecture is designed to be flexible and evolvable. We can iterate as we learn.*
