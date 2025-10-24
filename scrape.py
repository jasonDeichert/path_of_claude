#!/usr/bin/env python3
"""
CLI tool for scraping POE.ninja build data.

Usage:
    # Scrape top builds from hour-3 snapshot
    python scrape.py mercenarieshcssf hour-3

    # Scrape and filter by ascendancy
    python scrape.py mercenarieshcssf hour-3 --ascendancy Berserker

    # Export POB codes for top 5 builds
    python scrape.py mercenarieshcssf hour-3 --ascendancy Berserker --export-pob 5

    # Save snapshot to JSON
    python scrape.py mercenarieshcssf hour-3 --output builds/hour-3.json
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scraper import PoeNinjaScraper


def main():
    parser = argparse.ArgumentParser(
        description="Scrape build data from poe.ninja",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape hour-3 snapshot for HC SSF
  python scrape.py mercenarieshcssf hour-3

  # Filter for Berserkers only
  python scrape.py mercenarieshcssf hour-3 --ascendancy Berserker

  # Export POB codes for top 5 builds
  python scrape.py mercenarieshcssf hour-3 --ascendancy Berserker --export-pob 5

  # Save to JSON file
  python scrape.py mercenarieshcssf hour-3 --output builds/hour-3.json
        """,
    )

    parser.add_argument("league", help="League identifier (e.g., mercenarieshcssf)")
    parser.add_argument(
        "snapshot",
        nargs="?",
        default="latest",
        help="Time snapshot (latest, hour-3, day-1, week-1, etc.)",
    )
    parser.add_argument(
        "--ascendancy", "-a", help="Filter by ascendancy (e.g., Berserker)"
    )
    parser.add_argument(
        "--min-level", type=int, help="Minimum character level"
    )
    parser.add_argument(
        "--max-level", type=int, help="Maximum character level"
    )
    parser.add_argument(
        "--limit", "-l", type=int, help="Limit number of builds to scrape"
    )
    parser.add_argument(
        "--export-pob",
        "-p",
        type=int,
        metavar="N",
        help="Export POB codes for top N builds",
    )
    parser.add_argument(
        "--pob-output-dir",
        default="builds/pob_exports",
        help="Directory to save POB codes (default: builds/pob_exports)",
    )
    parser.add_argument(
        "--output", "-o", help="Save snapshot to JSON file"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Run browser in visible mode (for debugging)",
    )

    args = parser.parse_args()

    # Create scraper
    headless = args.headless and not args.visible
    scraper = PoeNinjaScraper(headless=headless)

    print("=" * 60)
    print(f"POE.ninja Build Scraper")
    print("=" * 60)
    print(f"League: {args.league}")
    print(f"Snapshot: {args.snapshot}")
    print("=" * 60 + "\n")

    # Phase 1: Scrape table
    snapshot = scraper.scrape_builds(
        league=args.league,
        snapshot=args.snapshot,
        limit=args.limit,
    )

    print(f"\n✓ Scraped {len(snapshot.builds)} builds")

    # Apply filters
    if args.ascendancy:
        snapshot = snapshot.filter_by_ascendancy(args.ascendancy)
        print(f"✓ Filtered to {len(snapshot.builds)} {args.ascendancy} builds")

    if args.min_level or args.max_level:
        snapshot = snapshot.filter_by_level(args.min_level, args.max_level)
        print(f"✓ Filtered to {len(snapshot.builds)} builds by level")

    # Display summary
    print("\n" + "=" * 60)
    print(f"Top {min(10, len(snapshot.builds))} Builds:")
    print("=" * 60)

    for i, build in enumerate(snapshot.top(10), 1):
        print(
            f"{i:2}. [{build.ascendancy:15}] Lv{build.level:3} - {build.character_name:25} "
            f"| Life: {build.life:5} | EHP: {build.effective_hp//1000:3}k | "
            f"{build.main_skill}"
        )

    # Phase 2: Export POB codes if requested
    if args.export_pob:
        top_n = snapshot.top(args.export_pob)
        print(f"\n{'=' * 60}")
        print(f"Exporting POB codes for top {len(top_n)} builds...")
        print("=" * 60)

        pob_codes = scraper.export_pob_codes(top_n, output_dir=args.pob_output_dir)

        if pob_codes:
            print(f"\n✓ POB codes saved to: {args.pob_output_dir}/")

    # Save snapshot if requested
    if args.output:
        scraper.save_snapshot(snapshot, args.output)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
