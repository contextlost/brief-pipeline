#!/usr/bin/env python3
"""rss-story-cluster: fetch RSS feeds, group items into stories, rank by breadth.

Usage:
    cp feeds.example.yaml feeds.yaml   # then edit in your feeds
    pip install -r requirements.txt
    python main.py
"""
import sys

from config import load_config
from rss_fetcher import fetch_all
from cluster import cluster_items
from rank import rank_clusters


def main() -> int:
    try:
        config = load_config()
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    items = fetch_all(config["feeds"], config["settings"]["max_items_per_feed"])
    if not items:
        print("no items fetched; check your feeds.", file=sys.stderr)
        return 1

    clusters = cluster_items(items, config["settings"]["similarity_threshold"])
    ranked = rank_clusters(clusters)

    print(f"\n{len(items)} items -> {len(ranked)} stories\n")
    for i, story in enumerate(ranked, 1):
        outlets = sorted({it["outlet"] for it in story})
        print(f"{i}. [{len(outlets)} outlets] {story[0]['title']}")
        for outlet in outlets:
            print(f"   - {outlet}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
