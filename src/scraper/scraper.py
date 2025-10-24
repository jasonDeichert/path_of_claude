"""Main scraper for poe.ninja build data."""

from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page
import time
import json
from pathlib import Path

from .models import Build, BuildSnapshot
from .parsing import (
    parse_number_with_suffix,
    extract_skill_name_from_url,
    extract_account_from_url,
    clean_keystone_name,
)


class PoeNinjaScraper:
    """
    Scrapes build data from poe.ninja with flexible parameterization.

    Supports two-phase scraping:
    - Phase 1: Table scraping for build overview
    - Phase 2: POB export extraction for detailed analysis
    """

    BASE_URL = "https://poe.ninja/builds"

    def __init__(self, headless: bool = True):
        """
        Initialize scraper.

        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.headless = headless

    def scrape_builds(
        self,
        league: str,
        snapshot: str = "latest",
        limit: Optional[int] = None,
    ) -> BuildSnapshot:
        """
        Scrape builds from poe.ninja table (Phase 1).

        Args:
            league: League identifier (e.g., "mercenarieshcssf")
            snapshot: Time snapshot ("latest", "hour-3", "day-1", "week-1", etc.)
            limit: Max number of builds to scrape (default: all visible, usually 100)

        Returns:
            BuildSnapshot with builds and metadata
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            # Construct URL
            url = f"{self.BASE_URL}/{league}"
            if snapshot != "latest":
                url += f"?timemachine={snapshot}"

            print(f"Loading: {url}")
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)  # Wait for table to render

            # Extract builds from table
            builds = self._extract_builds_from_table(page, limit)

            browser.close()

            return BuildSnapshot(
                league=league,
                snapshot=snapshot,
                builds=builds,
                total_builds=len(builds),
            )

    def _extract_builds_from_table(
        self, page: Page, limit: Optional[int] = None
    ) -> List[Build]:
        """Extract build data from table rows."""
        builds = []

        # Get all table rows
        rows = page.locator("tbody tr").all()
        total_rows = len(rows)

        if limit:
            rows = rows[:limit]

        print(f"Extracting {len(rows)} builds from table (total visible: {total_rows})...")

        for i, row in enumerate(rows):
            try:
                build = self._parse_build_row(row, rank=i + 1)
                builds.append(build)
            except Exception as e:
                print(f"Warning: Failed to parse row {i+1}: {e}")
                continue

        print(f"Successfully extracted {len(builds)} builds")
        return builds

    def _parse_build_row(self, row, rank: int) -> Build:
        """
        Parse a single build row from the table.

        Table structure:
        1. Name (link)
        2. Level (number + ascendancy img)
        3. Life (number)
        4. ES (number)
        5. EHP (number with suffix)
        6. DPS (number with suffix + skill gem img)
        7. Keystones (multiple imgs)
        """
        cells = row.locator("td").all()

        # Cell 1: Character name and profile URL
        name_link = cells[0].locator("a").first
        character_name = name_link.inner_text().strip()
        profile_url = name_link.get_attribute("href") or ""
        account_name = extract_account_from_url(profile_url)

        # Cell 2: Level and Ascendancy
        level_cell = cells[1]
        level_text = level_cell.inner_text().strip()
        # Extract just the number (there might be ascendancy name too)
        level = int(level_text.split()[0])

        # Get ascendancy from img alt
        ascendancy_img = level_cell.locator("img").first
        ascendancy = ascendancy_img.get_attribute("alt") or "Unknown"

        # Cell 3: Life
        life = parse_number_with_suffix(cells[2].inner_text().strip())

        # Cell 4: Energy Shield
        energy_shield = parse_number_with_suffix(cells[3].inner_text().strip())

        # Cell 5: Effective HP
        effective_hp = parse_number_with_suffix(cells[4].inner_text().strip())

        # Cell 6: DPS and Main Skill
        dps_cell = cells[5]
        dps_text = dps_cell.inner_text().strip()
        dps = parse_number_with_suffix(dps_text)

        # Get main skill from gem image
        skill_img = dps_cell.locator("img").first
        skill_url = skill_img.get_attribute("src") or ""
        main_skill = extract_skill_name_from_url(skill_url)

        # Cell 7: Keystones
        keystone_imgs = cells[6].locator("img").all()
        keystones = [
            clean_keystone_name(img.get_attribute("alt") or "")
            for img in keystone_imgs
        ]
        keystones = [k for k in keystones if k]  # Remove empty strings

        return Build(
            character_name=character_name,
            rank=rank,
            level=level,
            ascendancy=ascendancy,
            life=life,
            energy_shield=energy_shield,
            effective_hp=effective_hp,
            dps=dps,
            main_skill=main_skill,
            keystones=keystones,
            profile_url=profile_url,
            account_name=account_name,
        )

    def export_pob_code(self, build: Build) -> str:
        """
        Get POB code for a single build (Phase 2).

        Args:
            build: Build object with profile_url populated

        Returns:
            Base64-encoded POB import code
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            # Navigate to build detail page
            full_url = f"https://poe.ninja{build.profile_url}"
            print(f"Loading build details: {build.character_name}")
            page.goto(full_url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            # Extract POB code from input field
            pob_input = page.locator('input[aria-label*="Path of Building"]').first
            pob_code = pob_input.get_attribute("value") or ""

            browser.close()

            if not pob_code:
                raise ValueError(f"No POB code found for {build.character_name}")

            return pob_code

    def export_pob_codes(
        self, builds: List[Build], output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Extract POB codes for multiple builds (Phase 2 batch).

        Args:
            builds: List of Build objects to get POB codes for
            output_dir: Optional directory to save POB code files

        Returns:
            Dict mapping character_name -> pob_code
        """
        pob_codes = {}

        print(f"\nExporting POB codes for {len(builds)} builds...")

        for i, build in enumerate(builds, 1):
            try:
                print(f"[{i}/{len(builds)}] {build.character_name}...", end=" ")
                pob_code = self.export_pob_code(build)
                pob_codes[build.character_name] = pob_code
                print(f"✓ ({len(pob_code)} chars)")

                # Optional: save to file
                if output_dir:
                    self._save_pob_code(build.character_name, pob_code, output_dir)

                # Small delay to avoid hammering the server
                time.sleep(1)

            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        print(f"\nSuccessfully exported {len(pob_codes)}/{len(builds)} POB codes")
        return pob_codes

    def _save_pob_code(self, character_name: str, pob_code: str, output_dir: str):
        """Save POB code to file."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_name = "".join(c if c.isalnum() else "_" for c in character_name)
        filepath = output_path / f"{safe_name}.txt"

        with open(filepath, "w") as f:
            f.write(pob_code)

    def save_snapshot(self, snapshot: BuildSnapshot, output_path: str):
        """
        Save BuildSnapshot to JSON file.

        Args:
            snapshot: BuildSnapshot to save
            output_path: Path to output JSON file
        """
        # Convert to dict (dataclasses can't directly serialize)
        data = {
            "league": snapshot.league,
            "snapshot": snapshot.snapshot,
            "total_builds": snapshot.total_builds,
            "scraped_at": snapshot.scraped_at,
            "scraper_version": snapshot.scraper_version,
            "filters": {
                "ascendancy": snapshot.ascendancy_filter,
                "min_level": snapshot.min_level,
                "max_level": snapshot.max_level,
            },
            "builds": [
                {
                    "rank": b.rank,
                    "character_name": b.character_name,
                    "account_name": b.account_name,
                    "level": b.level,
                    "ascendancy": b.ascendancy,
                    "life": b.life,
                    "energy_shield": b.energy_shield,
                    "effective_hp": b.effective_hp,
                    "dps": b.dps,
                    "main_skill": b.main_skill,
                    "keystones": b.keystones,
                    "profile_url": b.profile_url,
                }
                for b in snapshot.builds
            ],
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Saved snapshot to: {output_path}")
