#!/usr/bin/env python3
"""brief-pipeline: RSS feeds -> ranked stories -> narrated edition (JSON + HTML).

Usage:
    cp feeds.example.yaml feeds.yaml   # then edit in your feeds
    pip install -r requirements.txt
    python main.py                      # extractive narrator, no keys needed

    # Upgrade the writer to full narratives with any OpenAI-compatible API:
    cp .env.example .env               # then set LLM_API_KEY
    python main.py
"""
import sys
from datetime import date
from pathlib import Path

from config import load_config
from rss_fetcher import fetch_all
from cluster import cluster_items
from rank import rank_clusters
from edition import save_edition, load_latest, diff_editions
from writer import ExtractiveNarrator, LLMNarrator
from format import render_html

ROOT = Path(__file__).resolve().parent


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

    ranked = rank_clusters(
        cluster_items(items, config["settings"]["similarity_threshold"]))
    print(f"\n{len(items)} items -> {len(ranked)} stories")

    prior = load_latest(ROOT)
    new, continuing = diff_editions(prior, ranked)
    print(f"{len(new)} new, {len(continuing)} continuing since last edition")

    if config["llm"]["api_key"]:
        narrator = LLMNarrator(config["llm"])
        print("writer: LLM narrator")
    else:
        narrator = ExtractiveNarrator()
        print("writer: extractive narrator (set LLM_API_KEY for full narratives)")

    brief = narrator.narrate(new, continuing)
    edition = {
        "date": date.today().isoformat(),
        "narrator": narrator.name,
        "paragraphs": brief["paragraphs"],
        "references": brief["references"],
        "stories": [[{"title": i["title"], "outlet": i["outlet"], "link": i["link"]}
                     for i in story] for story in ranked],
        "counts": {"items": len(items), "stories": len(ranked),
                   "new": len(new), "continuing": len(continuing)},
    }
    saved = save_edition(ROOT, edition)
    html_path = saved.with_suffix(".html")
    html_path.write_text(render_html(edition), encoding="utf-8")

    print(f"\nsaved {saved.name} + {html_path.name}\n")
    print("\n\n".join(edition["paragraphs"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
