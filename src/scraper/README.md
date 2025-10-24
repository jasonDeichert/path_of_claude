# POE.ninja Scraper

## Current Status

**Working:** Basic navigation to any league's build page

**Not Yet Implemented:**
- Data extraction from build table
- Pagination handling
- Error handling / retries
- Rate limiting
- Data validation

## Usage

```bash
# Default: Mercenaries HC SSF
python poe_builds_scraper.py

# Specific league
python poe_builds_scraper.py settlershcssf

# Headless mode
python poe_builds_scraper.py keepershcssf --headless
```

## Next Steps

1. Extract build data from table
2. Handle pagination (if multiple pages)
3. Save to structured JSON format
4. Add error handling
5. Implement caching

## Dependencies

```bash
pip install playwright
playwright install chromium
```
