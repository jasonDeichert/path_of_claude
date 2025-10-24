#!/usr/bin/env python3
"""
Analyze meta statistics from scraped build data.

Shows:
- Most played ascendancies
- Most used skills
- Ascendancy -> skill combinations
- Progression (what skills/ascendancies dominated at different times)
"""

import sys
from pathlib import Path
from collections import Counter
from typing import List

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scraper import PoeNinjaScraper, BuildSnapshot


def analyze_snapshot(snapshot: BuildSnapshot, label: str):
    """Analyze a single snapshot and print statistics."""
    print(f"\n{'='*70}")
    print(f"{label} - {snapshot.league} ({len(snapshot.builds)} builds)")
    print(f"{'='*70}")

    # Count ascendancies
    ascendancy_counts = Counter(b.ascendancy for b in snapshot.builds)
    print(f"\nTop Ascendancies:")
    for asc, count in ascendancy_counts.most_common(10):
        pct = (count / len(snapshot.builds)) * 100
        print(f"  {asc:20} {count:3} ({pct:5.1f}%)")

    # Count skills
    skill_counts = Counter(b.main_skill for b in snapshot.builds)
    print(f"\nTop Skills:")
    for skill, count in skill_counts.most_common(10):
        pct = (count / len(snapshot.builds)) * 100
        print(f"  {skill:25} {count:3} ({pct:5.1f}%)")

    # Top ascendancy + skill combos
    combo_counts = Counter((b.ascendancy, b.main_skill) for b in snapshot.builds)
    print(f"\nTop Ascendancy + Skill Combos:")
    for (asc, skill), count in combo_counts.most_common(10):
        pct = (count / len(snapshot.builds)) * 100
        print(f"  {asc:15} + {skill:25} {count:3} ({pct:5.1f}%)")

    # Average level
    avg_level = sum(b.level for b in snapshot.builds) / len(snapshot.builds)
    print(f"\nAverage Level: {avg_level:.1f}")

    # Level distribution
    level_ranges = {
        "40-59": len([b for b in snapshot.builds if 40 <= b.level < 60]),
        "60-69": len([b for b in snapshot.builds if 60 <= b.level < 70]),
        "70-79": len([b for b in snapshot.builds if 70 <= b.level < 80]),
        "80-89": len([b for b in snapshot.builds if 80 <= b.level < 90]),
        "90-99": len([b for b in snapshot.builds if 90 <= b.level < 100]),
        "100": len([b for b in snapshot.builds if b.level == 100]),
    }
    print(f"\nLevel Distribution:")
    for range_name, count in level_ranges.items():
        pct = (count / len(snapshot.builds)) * 100 if snapshot.builds else 0
        print(f"  {range_name:10} {count:3} ({pct:5.1f}%)")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Analyze meta from scraped builds")
    parser.add_argument("league", help="League to analyze (e.g., mercenarieshcssf)")
    parser.add_argument(
        "snapshots",
        nargs="+",
        help="Snapshots to analyze (e.g., hour-3 hour-6 day-1 week-1)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of builds to scrape per snapshot (default: 100)",
    )

    args = parser.parse_args()

    scraper = PoeNinjaScraper(headless=True)

    print("="*70)
    print(f"Meta Analysis: {args.league}")
    print("="*70)

    # Scrape and analyze each snapshot
    for snapshot_name in args.snapshots:
        print(f"\nScraping {snapshot_name}...")
        snapshot = scraper.scrape_builds(args.league, snapshot_name, limit=args.limit)
        analyze_snapshot(snapshot, snapshot_name.upper())

    # Summary comparison if multiple snapshots
    if len(args.snapshots) > 1:
        print(f"\n\n{'='*70}")
        print("PROGRESSION SUMMARY")
        print(f"{'='*70}")

        print("\nHow did top ascendancies change over time?")
        # This would require storing snapshots and comparing
        # For now, just note that user can see trends from the individual analyses above


if __name__ == "__main__":
    main()
