"""Edition persistence + diffing: what is genuinely new since last time?"""
import json
import re
from datetime import date
from pathlib import Path

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _edition_dir(root):
    return Path(root) / "editions"


def save_edition(root, edition):
    d = _edition_dir(root)
    d.mkdir(exist_ok=True)
    stamp = edition.get("date") or date.today().isoformat()
    path = d / f"{stamp}.json"
    path.write_text(json.dumps(edition, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_latest(root):
    d = _edition_dir(root)
    if not d.exists():
        return None
    files = sorted(d.glob("*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))


def _story_key(story):
    return {t for t in _TOKEN_RE.findall(story[0]["title"].lower()) if len(t) > 3}


def _overlap(a, b):
    return len(a & b) / max(len(a | b), 1)


def diff_editions(prior, ranked):
    """Split ranked stories into (new, continuing) versus the prior edition."""
    if not prior:
        return ranked, []
    prior_keys = [_story_key(s) for s in prior.get("stories", [])]
    new, continuing = [], []
    for story in ranked:
        key = _story_key(story)
        if any(_overlap(key, pk) >= 0.4 for pk in prior_keys):
            continuing.append(story)
        else:
            new.append(story)
    return new, continuing
