#!/usr/bin/env python3
"""
Example: Analyze early league progression for a specific ascendancy.

This shows how builds progress from hour 3 -> hour 6 -> hour 12,
which is valuable for understanding realistic league start paths.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scraper import PoeNinjaScraper


def main():
    # Configuration
    LEAGUE = "mercenarieshcssf"  # Previous league for analysis
    ASCENDANCY = "Berserker"
    TOP_N = 5  # Look at top 5 builds at each snapshot

    scraper = PoeNinjaScraper(headless=True)

    print("=" * 70)
    print(f"Early League Progression Analysis: {ASCENDANCY}")
    print("=" * 70)

    # Collect snapshots from different time points
    snapshots = {}
    for time in ["hour-3", "hour-6", "hour-12"]:
        print(f"\nScraping {time} snapshot...")
        snapshot = scraper.scrape_builds(LEAGUE, time, limit=50)

        # Filter for our ascendancy
        filtered = snapshot.filter_by_ascendancy(ASCENDANCY)
        snapshots[time] = filtered

        print(f"  Found {len(filtered.builds)} {ASCENDANCY} builds")

    # Display progression
    print("\n" + "=" * 70)
    print(f"Top {TOP_N} {ASCENDANCY} Progression:")
    print("=" * 70)

    for time in ["hour-3", "hour-6", "hour-12"]:
        snapshot = snapshots[time]
        print(f"\n{time.upper()}:")
        print("-" * 70)

        for i, build in enumerate(snapshot.top(TOP_N), 1):
            print(
                f"  {i}. Lv{build.level:2} - {build.character_name:25} | "
                f"Life: {build.life:4} | EHP: {build.effective_hp//1000:2}k | "
                f"{build.main_skill}"
            )

    # Export POB codes for detailed analysis
    print("\n" + "=" * 70)
    print("Exporting POB codes for top builds at each snapshot...")
    print("=" * 70)

    for time in ["hour-3", "hour-6", "hour-12"]:
        snapshot = snapshots[time]
        top_builds = snapshot.top(TOP_N)

        output_dir = f"builds/pob_exports/{time}"
        print(f"\n{time}:")
        pob_codes = scraper.export_pob_codes(top_builds, output_dir=output_dir)
        print(f"  ✓ Saved {len(pob_codes)} POB codes to {output_dir}/")

    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Import POB codes into Path of Building desktop app")
    print("  2. Compare passive trees between hour-3 and hour-12")
    print("  3. Note skill gem progressions")
    print("  4. Identify key gear pieces acquired by hour 12")
    print("  5. Plan your own league start based on these realistic paths")


if __name__ == "__main__":
    main()
