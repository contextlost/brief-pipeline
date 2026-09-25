"""Fetch and parse RSS/Atom feeds with feedparser."""
import feedparser


def fetch_feed(url, max_items=20):
    """Return (outlet_name, [items]). A bad feed yields no items, never an error."""
    parsed = feedparser.parse(url)
    outlet = (parsed.feed.get("title") or url).strip() or url
    items = []
    for entry in parsed.entries[:max_items]:
        title = (entry.get("title") or "").strip()
        if not title:
            continue
        items.append({
            "title": title,
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": (entry.get("summary") or entry.get("description") or "").strip(),
            "outlet": outlet,
        })
    return outlet, items


def fetch_all(feeds, max_items=20):
    """feeds: [{name, url}]. Returns a flat list of items tagged with outlet."""
    all_items = []
    for feed in feeds:
        url = feed.get("url", "")
        label = feed.get("name") or url
        try:
            outlet, items = fetch_feed(url, max_items)
            for it in items:
                it["outlet"] = feed.get("name") or outlet
            all_items.extend(items)
            print(f"  {label}: {len(items)} items")
        except Exception as exc:  # network hiccups shouldn't kill the run
            print(f"  {label}: skipped ({exc})")
    return all_items
