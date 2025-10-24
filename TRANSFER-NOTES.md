# Transfer Notes

## Ready for New Repo

Everything in this `repo-ready/` directory is organized and ready to move to a new repository.

## File Structure

```
repo-ready/
├── README.md                      # Main project readme
├── ROADMAP.md                     # Development phases
├── requirements.txt               # Python dependencies
├── .gitignore                     # Standard ignores
├── docs/
│   ├── PROJECT-VISION.md         # Detailed vision and use cases
│   └── ARCHITECTURE.md           # Technical architecture decisions
├── src/
│   └── scraper/
│       ├── poe_builds_scraper.py # Working Playwright scraper
│       └── README.md             # Scraper documentation
└── examples/
    ├── 3.27-patch-notes-official.txt
    └── 3.27-patch-notes-summary.md

```

## What's Working

✅ **Basic scraper** - Can navigate to any league on poe.ninja
- Tested with: mercenarieshcssf, settlershcssf, keepershcssf
- Headless and visible modes
- Clean Python code

✅ **Documentation** - Comprehensive planning docs
- Vision with use cases
- Technical architecture
- Development roadmap
- All design decisions documented

## What's Not Done

❌ Data extraction (scraper only navigates, doesn't extract table data)
❌ POB integration (submodule not added yet)
❌ Filtering/analysis
❌ CLI interface

## Next Steps After Transfer

1. **Initialize git repo:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Project foundation"
   ```

2. **Add POB submodule:**
   ```bash
   git submodule add https://github.com/PathOfBuildingCommunity/PathOfBuilding pob
   git commit -m "Add Path of Building as submodule"
   ```

3. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Test scraper:**
   ```bash
   python src/scraper/poe_builds_scraper.py mercenarieshcssf
   ```

5. **Start Phase 1 development:**
   - Extract build data from table
   - Define JSON schema
   - Save snapshots

## Design Principles Established

1. **POB as submodule** - Use their code, don't fork
2. **Playwright over API** - Simpler, more maintainable
3. **Multi-language** - Python for scraping, Lua for POB integration
4. **JSON bridge** - Language-agnostic data format
5. **HC SSF first** - Default to hardcore viable builds

## Open Questions (For Future)

- License? (Probably MIT)
- Rate limiting strategy?
- Data storage: JSON vs SQLite?
- CLI framework: Click vs native Lua?

## Original Context

This started as personal league prep for POE 3.27 "Keepers of the Flame" and evolved into a tool concept. The seed documents capture the initial vision and working proof of concept.

---

**Everything here is ready to copy to a new repository and start development.**
