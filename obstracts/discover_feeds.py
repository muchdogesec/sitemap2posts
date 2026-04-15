#!/usr/bin/env python3
"""
Discover feed configuration files and generate a matrix for GitHub Actions.

This script finds all feed config JSON files in the obstracts/config directory
and outputs them in a format suitable for GitHub Actions matrix strategy.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse


def discover_feed_configs(
    base_dir: Path, include_dirs: List[str] = None, filter_stems: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Discover all feed configuration files.

    Args:
        base_dir: Base directory containing feed configs
        include_dirs: List of subdirectories to include (default: ['main', 'issues'])
        filter_stems: List of file stems to filter by (default: None, include all)

    Returns:
        List of dictionaries containing feed metadata
    """
    if include_dirs is None:
        include_dirs = ["main", "issues"]

    feeds = []
    cwd = Path.cwd()

    for dir_name in include_dirs:
        config_dir = base_dir / dir_name

        if not config_dir.exists():
            print(f"Warning: Directory {config_dir} does not exist", file=sys.stderr)
            continue

        # Find all JSON files in the directory
        for config_file in sorted(config_dir.glob("*.json")):
            # Apply filter if provided
            if filter_stems and config_file.stem not in filter_stems:
                continue

            try:
                with open(config_file, "r") as f:
                    config_data = json.load(f)

                # Get relative path from current working directory
                try:
                    rel_path = config_file.relative_to(cwd)
                except ValueError:
                    # If file is outside cwd, use the path as-is
                    rel_path = config_file

                # Extract metadata
                feed_info = {
                    "config_path": str(rel_path),
                    "name": config_data.get("name", config_file.stem),
                    "feed_id": config_data.get("feed_id", ""),
                    "blog_url": config_data.get("blog_url", ""),
                    "category": dir_name,
                    "config_data": config_data,  # Store full config for --full mode
                }

                feeds.append(feed_info)

            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to read {config_file}: {e}", file=sys.stderr)
                continue

    return feeds


def generate_simple_matrix(feeds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a simple GitHub Actions matrix with basic metadata.

    Args:
        feeds: List of feed metadata dictionaries

    Returns:
        Dictionary containing the matrix configuration with metadata
    """
    # Create matrix with config paths and key metadata
    matrix = {
        "include": [
            {
                "config_path": feed["config_path"],
                "name": feed["name"],
                "feed_id": feed["feed_id"],
                "category": feed["category"],
            }
            for feed in feeds
        ]
    }

    return matrix


def generate_full_matrix(feeds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a full GitHub Actions matrix with complete config content.

    Args:
        feeds: List of feed metadata dictionaries

    Returns:
        Dictionary containing the matrix with full config objects
    """
    # Create matrix with full config content
    matrix = {
        "include": [
            {
                "config_path": feed["config_path"],
                "name": feed["name"],
                "feed_id": feed["feed_id"],
                "category": feed["category"],
                "config": feed.get("config_data", {}),
            }
            for feed in feeds
        ]
    }

    return matrix


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Discover feed configurations and generate GitHub Actions matrix.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate simple matrix (paths + metadata)
  python discover_feeds.py

  # Generate full matrix with entire config content
  python discover_feeds.py --full

  # Include only main feeds
  python discover_feeds.py --include main

  # Filter specific feeds by file stem
  python discover_feeds.py --filter specterops expel hunt

  # Combine filters and categories
  python discover_feeds.py --include main --filter specterops

  # List feeds (plain text)
  python discover_feeds.py --list

  # List feeds (markdown table)
  python discover_feeds.py --markdown

  # Set GitHub output
  python discover_feeds.py --github-output

  # Pretty print for debugging
  python discover_feeds.py --pretty
        """,
    )

    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path("obstracts/config"),
        help="Base directory containing feed configs (default: obstracts/config)",
    )

    parser.add_argument(
        "--include",
        nargs="+",
        default=["main", "issues"],
        help="Subdirectories to include (default: main issues)",
    )

    parser.add_argument(
        "--filter",
        nargs="+",
        metavar="STEM",
        help="Filter by specific feed file stems (e.g., specterops expel)",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Generate full matrix including entire config content (default: matrix with metadata only)",
    )

    parser.add_argument(
        "--github-output",
        action="store_true",
        help="Output in GitHub Actions output format",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all discovered feeds with details",
    )

    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Output discovered feeds in markdown format",
    )

    args = parser.parse_args()

    # Discover feeds
    feeds = discover_feed_configs(args.base_dir, args.include, args.filter)

    if not feeds:
        if args.filter:
            print(
                f"Error: No feed configurations found matching filters: {', '.join(args.filter)}",
                file=sys.stderr,
            )
        else:
            print("Error: No feed configurations found", file=sys.stderr)
        sys.exit(1)

    # List mode
    if args.list:
        print(f"Discovered {len(feeds)} feed(s):\n")
        for feed in feeds:
            print(f"  📄 {feed['name']}")
            print(f"     Path: {feed['config_path']}")
            print(f"     Feed ID: {feed['feed_id']}")
            print(f"     URL: {feed['blog_url']}")
            print(f"     Category: {feed['category']}")
            print()
        return

    # Markdown mode
    if args.markdown:
        print(f"# Discovered Feeds ({len(feeds)})\n")
        print("| Name | Feed ID | URL | Category | Config Path |")
        print("|------|---------|-----|----------|-------------|")
        for feed in feeds:
            # Escape pipe characters in fields
            name = feed['name'].replace('|', '\\|')
            feed_id_short = feed['feed_id'] if feed['feed_id'] else 'N/A'
            url = feed['blog_url'].replace('|', '\\|')
            category = feed['category']
            config_path = feed['config_path'].replace('|', '\\|')
            print(f"| {name} | `{feed_id_short}` | {url} | {category} | `{config_path}` |")
        return

    # Generate matrix
    if args.full:
        matrix = generate_full_matrix(feeds)
    else:
        matrix = generate_simple_matrix(feeds)

    # Output
    indent = 2 if args.pretty else None
    matrix_json = json.dumps(matrix, indent=indent)

    if args.github_output:
        # GitHub Actions output format
        print(f"matrix={matrix_json}")
    else:
        # Plain JSON
        print(matrix_json)


if __name__ == "__main__":
    main()
