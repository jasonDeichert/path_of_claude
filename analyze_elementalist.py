#!/usr/bin/env python3
"""
Analyze Elementalist builds for league start planning.

Scrapes multiple time snapshots and enriches with detailed skill/gear data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scraper import PoeNinjaScraper
import json


def analyze_elementalist_progression():
    """Scrape Elementalist builds across different time periods."""

    scraper = PoeNinjaScraper(headless=True)
    league = "mercenarieshcssf"

    time_periods = [
        ("hour-12", 5),  # Top 5 from hour-12
        ("day-1", 5),    # Top 5 from day-1
        ("week-1", 10),  # Top 10 from week-1
    ]

    all_results = {}

    for snapshot, limit in time_periods:
        print(f"\n{'='*60}")
        print(f"SNAPSHOT: {snapshot}")
        print(f"{'='*60}")

        # Scrape table data
        builds_snapshot = scraper.scrape_builds(league, snapshot)

        # Filter to Elementalists
        elementalist_builds = builds_snapshot.filter_by_ascendancy("Elementalist")

        if len(elementalist_builds.builds) == 0:
            print(f"No Elementalist builds found in {snapshot}")
            continue

        print(f"\nFound {len(elementalist_builds.builds)} Elementalist builds")
        print(f"Taking top {min(limit, len(elementalist_builds.builds))}...")

        top_builds = elementalist_builds.top(limit)

        # Enrich with detailed information
        enriched_builds = scraper.enrich_builds_batch(top_builds)

        # Store results
        all_results[snapshot] = enriched_builds

        # Print summary
        print(f"\n{snapshot.upper()} ELEMENTALIST BUILDS:")
        print(f"{'='*60}")

        for i, build in enumerate(enriched_builds, 1):
            print(f"\n{i}. {build.character_name} (Lv{build.level})")
            print(f"   Life: {build.life:,} | ES: {build.energy_shield:,} | EHP: {build.effective_hp//1000}k")
            print(f"   Main Skill: {build.main_skill}")
            print(f"   Keystones: {', '.join(build.keystones) if build.keystones else 'None visible'}")

            if build.skill_groups:
                print(f"   Skill Setups:")
                for sg in build.skill_groups:
                    if sg.main_skill:
                        supports = [g.name for g in sg.gems if g.is_support]
                        print(f"     - {sg.main_skill}")
                        if supports:
                            for sup in supports:
                                print(f"       + {sup}")

    # Save detailed results
    output_dir = Path("planning/elementalist_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save each snapshot
    for snapshot, builds in all_results.items():
        output_file = output_dir / f"{snapshot}_detailed.json"

        # Convert to serializable format
        builds_data = []
        for build in builds:
            build_dict = {
                "character_name": build.character_name,
                "rank": build.rank,
                "level": build.level,
                "ascendancy": build.ascendancy,
                "life": build.life,
                "energy_shield": build.energy_shield,
                "effective_hp": build.effective_hp,
                "dps": build.dps,
                "main_skill": build.main_skill,
                "keystones": build.keystones,
                "skill_groups": [
                    {
                        "main_skill": sg.main_skill,
                        "gems": [{"name": g.name, "is_support": g.is_support} for g in sg.gems],
                        "link_count": sg.link_count
                    }
                    for sg in build.skill_groups
                ],
                "profile_url": build.profile_url
            }
            builds_data.append(build_dict)

        with open(output_file, 'w') as f:
            json.dump(builds_data, f, indent=2)

        print(f"\nSaved {snapshot} data to: {output_file}")

    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Data saved to: {output_dir}/")


if __name__ == "__main__":
    analyze_elementalist_progression()
