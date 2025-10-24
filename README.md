# POE Build Intelligence Tool

> **Status:** 🌱 Early development - Core concepts being validated

An intelligent build analysis tool for Path of Exile that helps you make informed decisions throughout the league lifecycle.

## The Problem

League start in Path of Exile (especially HC SSF) requires making build decisions with incomplete information:
- **Pre-league:** What worked last league? What got buffed/nerfed?
- **Early league:** What's actually working for other players?
- **Mid-league:** I found a unique - what builds use it?
- **Adaptation:** My build isn't working - what can I pivot to?

Current solutions are manual, time-consuming, and don't leverage Path of Building's powerful calculations.

## The Vision

A tool that combines:
- **poe.ninja** data (what people are actually playing)
- **Path of Building** calculations (actual build performance)
- **Smart filtering** (find builds you can actually play right now)

See [docs/PROJECT-VISION.md](docs/PROJECT-VISION.md) for detailed vision and roadmap.

## Current Status

**What exists:**
- ✅ Basic Playwright scraper (can navigate to any league)
- ✅ Project vision and architecture planning
- ✅ Proof of concept that this approach works

**What doesn't exist yet:**
- ❌ Data extraction from poe.ninja
- ❌ Path of Building integration
- ❌ Filtering/analysis features
- ❌ CLI interface

## Architecture Plan

```
poe-build-intel/
├── pob/                    # Submodule: PathOfBuilding repo
├── src/
│   ├── scraper/           # Python: poe.ninja data collection
│   └── pob-integration/   # Lua: Use POB's calculation engine
├── cli/                   # User interface
└── docs/                  # Documentation
```

**Key Design Decision:** Use Path of Building as a git submodule, require their Lua modules directly. This gives us:
- Latest game data (passive tree, gems, items)
- Full calculation engine (DPS, EHP, etc.)
- Automatic updates when POB releases new versions
- No need to maintain game data ourselves

## Quick Start (When Ready)

*Not functional yet - placeholder for future:*

```bash
# Install
git clone <repo>
cd poe-build-intel
git submodule update --init  # Get POB

# Scrape current league meta
python src/scraper/scrape.py --league keepershcssf

# Find builds using a specific unique
lua src/analyze.lua --item "Poet's Pen"

# Compare your build to meta
lua src/compare.lua --my-build exports/my_char.xml
```

## Use Cases

1. **Pre-league planning** - Analyze previous league + patch notes
2. **Meta tracking** - See what's working early in league
3. **Build pivot** - Find alternatives when your build isn't working
4. **Item discovery** - "I found X, what builds use it?"
5. **Optimization** - Compare your build to successful similar builds

## Contributing

Not ready for external contributions yet - still validating core concepts.

Once we have MVP:
- Issues for feature requests
- PRs welcome
- Code of conduct TBD

## Tech Stack

- **Scraping:** Python + Playwright
- **POB Integration:** Lua (require POB modules)
- **Data:** JSON intermediate format
- **CLI:** TBD (Python Click or Lua)

## License

TBD - Likely MIT

## Acknowledgments

- [poe.ninja](https://poe.ninja) - Build data source
- [Path of Building Community](https://github.com/PathOfBuildingCommunity/PathOfBuilding) - Calculations and game data
- Grinding Gear Games - Path of Exile

---

*This is an early-stage project. Everything is subject to change.*
