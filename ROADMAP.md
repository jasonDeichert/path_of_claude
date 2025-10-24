# Development Roadmap

## Phase 0: Foundation ✅ (Current)
- [x] Project structure
- [x] Vision documentation
- [x] Basic Playwright scraper (navigation only)
- [x] Architecture decisions documented

## Phase 1: MVP - Data Collection
**Goal:** Scrape and save league snapshots

**Tasks:**
- [ ] Extract build data from poe.ninja table
- [ ] Define JSON schema for builds
- [ ] Handle pagination
- [ ] Save snapshots with timestamps
- [ ] Add error handling and retries
- [ ] Implement rate limiting / caching

**Deliverable:** `python scrape.py keepershcssf` → `data/snapshots/keepershcssf_20251031.json`

## Phase 2: POB Integration
**Goal:** Use Path of Building calculations

**Tasks:**
- [ ] Add POB as git submodule
- [ ] Write Lua bridge to load POB modules
- [ ] Parse POB XML format
- [ ] Generate POB import codes from scraped data
- [ ] Run calculations on builds
- [ ] Export enhanced data

**Deliverable:** Builds augmented with real DPS/EHP calculations

## Phase 3: Analysis & Filtering
**Goal:** Query and filter builds

**Tasks:**
- [ ] Build filtering system (by class, skill, items, etc.)
- [ ] Meta analysis (popularity trends)
- [ ] Build comparison logic
- [ ] Similarity scoring

**Deliverable:** `filter.py --ascendancy Juggernaut --item "Kaom's Heart"`

## Phase 4: CLI Interface
**Goal:** Pleasant command-line experience

**Tasks:**
- [ ] CLI framework (Click or similar)
- [ ] Interactive mode
- [ ] Pretty output formatting
- [ ] Help documentation
- [ ] Examples

**Deliverable:** User-friendly CLI tool

## Phase 5: Advanced Features
**Goal:** Killer features nobody else has

**Tasks:**
- [ ] "Build Evolution" tracker (meta over time)
- [ ] "Builds I can play" (match current gear/tree)
- [ ] Character import from POE API
- [ ] Patch notes integration
- [ ] Passive tree overlap calculator

**Deliverable:** Unique value propositions

## Future Considerations

- Web interface?
- Shared build database?
- Discord bot?
- POB plugin/addon?

---

**Current Focus:** Phase 1 - Get data extraction working
