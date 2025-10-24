# POE Build Intelligence Tool - Project Vision

## Problem Statement

League start in Path of Exile (especially HC SSF) requires making build decisions with incomplete information:
- **Pre-league:** What worked last league? What got buffed/nerfed?
- **Day 1-3:** What's actually working for early players?
- **Mid-league:** I found a unique - what builds use it?
- **Adaptation:** My build isn't working - what can I pivot to with my current gear?

Current solutions are manual and time-consuming:
- Browse poe.ninja manually
- Search forums/Reddit for build guides
- No easy way to filter by "builds I can actually play right now"

## Vision

**An intelligent build analysis tool that helps you make informed decisions throughout the league lifecycle.**

### Core Capabilities

1. **Meta Analysis**
   - Scrape poe.ninja build data
   - Track popularity trends over time
   - Compare league metas (what changed from 3.26 → 3.27?)

2. **Smart Filtering**
   - Find builds by: class, skill, unique items, keystones
   - "Show me builds using [unique I just found]"
   - "Show me HC SSF viable builds with <5 div budget"
   - Filter by progression stage (league start vs endgame)

3. **Build Comparison**
   - Side-by-side build analysis
   - See what differs between similar builds
   - Identify gear/passive tree variations

4. **Path of Building Integration** (Stretch Goal)
   - Export builds to POB format
   - Import your current POB to find upgrade paths
   - "My current build vs meta builds" comparison

## Use Cases

### Pre-League Planning
**Actor:** Player preparing for league start
**Goal:** Choose a build based on what worked previously and patch changes

**Flow:**
1. Analyze previous league (settlershcssf) meta
2. Cross-reference with patch notes (what got nerfed?)
3. Identify 3-5 viable starters
4. Save shortlist for evaluation

### Early League Meta Tracking
**Actor:** Player in first week of league
**Goal:** See what's working for early adopters

**Flow:**
1. Day 3: Check keepershcssf meta
2. Compare to pre-league expectations
3. Identify surprising performers
4. Decide if current build choice is viable

### Mid-League Adaptation
**Actor:** Player who found a build-enabling unique
**Goal:** Find builds that can use this item

**Flow:**
1. Input unique item: "Poet's Pen"
2. Filter builds using this item
3. See which are HC SSF viable
4. Export top 3 to POB for detailed review

### Build Pivot
**Actor:** Player whose build isn't working
**Goal:** Find alternative build using existing gear

**Flow:**
1. Input current ascendancy, level, key items
2. Find builds matching constraints
3. Compare passive tree overlap (minimize regret costs)
4. Identify closest viable build

## Technical Approach

### Phase 1: Data Collection (Current)
- [x] Basic Playwright scraper
- [ ] Extract build table data
- [ ] Save to structured format (JSON)
- [ ] Handle pagination

### Phase 2: Data Analysis
- [ ] Parse build data into queryable format
- [ ] Build filtering system
- [ ] Meta trend analysis
- [ ] Comparison utilities

### Phase 3: Integration
- [ ] Path of Building export
- [ ] Patch notes integration
- [ ] Character import (from POE API)
- [ ] "Builds I can play" feature

### Phase 4: Interface
- [ ] CLI tool
- [ ] Web interface (maybe?)
- [ ] Export reports (markdown/PDF)

## Data Model (Draft)

```python
Build = {
    "character_name": str,
    "account_name": str,
    "class": str,              # e.g., "Marauder"
    "ascendancy": str,         # e.g., "Juggernaut"
    "level": int,
    "main_skill": str,
    "support_gems": List[str],
    "unique_items": List[str],
    "keystones": List[str],
    "life": int,
    "energy_shield": int,
    "dps": Optional[int],      # May not be available
    "last_updated": datetime,
    "league": str,
}

LeagueMeta = {
    "league": str,
    "snapshot_date": datetime,
    "total_builds": int,
    "builds": List[Build],
    "ascendancy_distribution": Dict[str, int],
    "skill_distribution": Dict[str, int],
    "unique_popularity": Dict[str, int],
}
```

## Key Design Principles

1. **Respect poe.ninja's Infrastructure**
   - Cache aggressively
   - Rate limit scraping
   - Don't hammer their servers
   - Acknowledge their data source

2. **Flexible & Extensible**
   - Support multiple leagues/timeframes
   - Easy to add new filters
   - Pluggable data sources (not just poe.ninja)

3. **League-Lifecycle Aware**
   - Different features for pre/during/post league
   - Understand progression (league start vs endgame builds)
   - Track meta evolution

4. **HC SSF First**
   - Default filters for HC viability
   - Assume no trading
   - Respect respec limits

## Open Questions

1. **Protobuf vs Playwright?**
   - Playwright: Easier, works today
   - Protobuf: Faster, more respectful of bandwidth
   - Decision: Start with Playwright, consider protobuf later

2. **How to handle "build viability"?**
   - Just popularity?
   - Include "reached level 95+"?
   - HC deaths tracked?

3. **Storage?**
   - Local JSON files?
   - SQLite database?
   - Cloud storage for sharing?

4. **POB Integration complexity?**
   - POB has XML format - parseable
   - But need passive tree data, skill gem data
   - May be significant effort

5. **Licensing?**
   - MIT? GPL?
   - How to credit poe.ninja?

## Success Criteria

**MVP (Minimum Viable Product):**
- [ ] Scrape current league build data
- [ ] Filter by ascendancy, skill, unique item
- [ ] Export top 20 builds to JSON
- [ ] Compare two league snapshots

**V1.0:**
- [ ] All MVP features
- [ ] CLI interface
- [ ] Meta trend tracking
- [ ] Export to markdown reports
- [ ] Documentation + examples

**V2.0:**
- [ ] Path of Building integration
- [ ] "Builds I can play" feature
- [ ] Character import from POE API
- [ ] Web interface

## Next Steps

1. Finish basic scraper (extract build data from table)
2. Define data models formally
3. Create sample output formats
4. Build filtering/query system
5. Package as installable tool

---

*This is a living document - will evolve as we learn more*
